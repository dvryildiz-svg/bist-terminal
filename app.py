import concurrent.futures
import datetime
import time
import uuid
from feedparser import parse
from isyatirimhisse import fetch_stock_data
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

# Türkiye Saat Dilimi (UTC+3) Sabiti
TZ_TR = datetime.timezone(datetime.timedelta(hours=3))

st.set_page_config(
    page_title="BİST & Çoklu Varlık Profesyonel Fon Yönetim Terminali",
    page_icon="🦁",
    layout="wide",
)

st.title("🦁 BİST & Çoklu Varlık Profesyonel Fon Yönetim Terminali")
st.markdown(
    "Tüm BİST Hisseleri Evreni, Sıralı Sinyaller, Gün İçi Fiyat Entegrasyonu,"
    " Sanal Portföy Grafikleri, Akıllı İşlem Panelleri ve **Dinamik Fiyatlı Zincir Emir Motoru**."
)

# GARANTİLİ WEBHOOK URL'NİZ
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz8Z6yiVGpGTmg2k3I3htQrkxVrKFpZFNeP7qjxxDS8mzrQ1B6LrTJ67q4Dokkh667LnQ/exec"

bist_hisseler = sorted([
    "ACSEL", "ADEL", "ADESE", "ADGYO", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT", "AGYO",
    "AHGAZ", "AKBNK", "AKCNS", "AKENR", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN",
    "AKSGY", "AKSUE", "ALARK", "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALGYO", "ALKA", "ALKIM",
    "ALMAD", "ALTNY", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARASE", "ARCLK", "ARDYZ", "ARENA",
    "ARSAN", "ARTMS", "ARZUM", "ASELS", "ASTOR", "ATAHN", "ATAKP", "ATEKS", "ATLAS", "ATSYH",
    "AVGYO", "AVOD", "AVTUR", "AYCES", "AYDEM", "AYEN", "AYES", "AYGAZ", "AZTEK", "BAGFS",
    "BAKAB", "BALAT", "BANVT", "BARMA", "BASCM", "BASGZ", "BAYRK", "BEGYO", "BERA", "BEYAZ",
    "BIENY", "BIGCH", "BIMAS", "BINHO", "BIOEN", "BIZIM", "BJKAS", "BLCYT", "BMSCH", "BNTAS",
    "BOBET", "BORLS", "BOSSA", "BRISA", "BRKO", "BRKSN", "BRSAN", "BRYAT", "BUCIM", "BURCE",
    "BURVA", "BVSAN", "BYDNR", "CANTE", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CEOEM", "CIMSA",
    "CLEBI", "CMBTN", "CMENT", "CONSE", "COSMO", "CRDFA", "CRFSA", "CUSAN", "CWENE", "DAGI",
    "DAPGM", "DARDL", "DENGE", "DERHL", "DERIM", "DESA", "DESPC", "DEVA", "DIRIT", "DITAS",
    "DMRGD", "DMSAS", "DNISI", "DOAS", "DOBUR", "DOCO", "DOFER", "DOGUB", "DOHOL", "DOKTA",
    "DSTKF", "DURDO", "DYOBY", "DZGYO", "EBEBK", "ECZYT", "EDIP", "EGEEN", "EGEPO", "EGGUB",
    "EGPRO", "EGSER", "EKGYO", "EKOS", "EKSUN", "ELITE", "EMKEL", "ENERY", "ENKAI", "ENSRI",
    "EPLAS", "ERBOS", "ERCB", "EREGL", "ERSU", "ESCAR", "ESCOM", "ESEN", "ETILR", "EUPWR",
    "EUREN", "EYGYO", "FADE", "FENER", "FLAP", "FMIZP", "FONET", "FORMT", "FORTE", "FRIGO",
    "FROTO", "GARAN", "GEDIK", "GEDZA", "GENIL", "GENTS", "GEREL", "GESAN", "GLCVY", "GLRYH",
    "GLYHO", "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL", "GSDDE", "GSDHO",
    "GSRAY", "GUBRF", "GWIND", "GZNMI", "HALKB", "HATEK", "HATSN", "HEDEF", "HEKTS", "HKTM",
    "HLGYO", "HTTBT", "HUBVC", "HURGZ", "ICBCT", "IDEAS", "IDGYO", "IHEVA", "IHGZT", "IHLAS",
    "IHLGM", "IHYAY", "IMASM", "INDES", "INFO", "INGRM", "INTEM", "INVEO", "IPEKE", "ISATR",
    "ISBIR", "ISBTR", "ISCTR", "ISDMR", "ISFIN", "ISGSY", "ISGYO", "ISKPL", "ISKUR", "ISMEN",
    "ISSEN", "IZENR", "IZFAS", "IZINV", "JANTS", "KAPLM", "KAREL", "KARSN", "KARTN", "KARYE",
    "KATMR", "KAYSE", "KBORU", "KCAER", "KCHOL", "KENT", "KERVT", "KFEIN", "KGYO", "KIMMR",
    "KLGYO", "KLKIM", "KLSYN", "KMPUR", "KNFRT", "KONKA", "KONTR", "KONYA", "KOPOL", "KORDS",
    "KOZAA", "KOZAL", "KRDMD", "KRGYO", "KRONT", "KRPLS", "KRSTL", "KRTEK", "KZBGY", "KZGYO",
    "LIDER", "LIDFA", "LKMNH", "LOGO", "LUKSK", "MAALT", "MACKO", "MAGEN", "MAKIM", "MAKTK",
    "MANAS", "MARKA", "MARTI", "MAVI", "MEDTR", "MEGAP", "MEKAG", "MERCN", "MERIT", "MERKO",
    "METRO", "METUR", "MGROS", "MIATK", "MMCAS", "MNDRS", "MNDTR", "MOBTL", "MPARK", "MRGYO",
    "MRSHL", "MSGYO", "MTRKS", "NIBAS", "NTGAZ", "NTHOL", "NUGYO", "NUHCM", "OBASE", "ODAS",
    "OFSYM", "ONCSM", "ORCAY", "ORGE", "ORMA", "OSMEN", "OSTIM", "OTKAR", "OYAKC", "OYYAT",
    "OZATD", "OZGYO", "OZKGY", "OZLRD", "OZRDN", "PAGYO", "PAMEL", "PARSN", "PASEU", "PCILT",
    "PEKGY", "PENGD", "PENTA", "PETKM", "PETUN", "PGSUS", "PINSU", "PKART", "PKENT", "PNSUT",
    "POLHO", "POLTK", "PRDGS", "PRKME", "PRKTS", "PRZMA", "PSDTC", "QUAGR", "RALYH", "RAYSG",
    "REYYR", "RNPOL", "RODRG", "ROYAL", "RTALB", "RUBNS", "RYGYO", "RYSAS", "SAFKR", "SAHOL",
    "SASA", "SAYAS", "SDTTR", "SEGMN", "SEGYO", "SEKFK", "SEKO", "SELEC", "SELGD", "SELVA",
    "SEYKM", "SILVR", "SISE", "SKBNK", "SKTAS", "SMART", "SMRTG", "SOKE", "SOKM", "SONME",
    "SUMAS", "SUNTK", "SURGY", "SUWEN", "TABGD", "TARKM", "TATEN", "TATGD", "TAVHL", "TBORG",
    "TCELL", "TCKRC", "TDGYO", "TEZOL", "TGSAS", "THYAO", "TKFEN", "TKNSA", "TLMAN", "TMPOL",
    "TMSN", "TOASO", "TRGYO", "TRILC", "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUPRS",
    "TUKAS", "TUREX", "TURGG", "UFUK", "ULAS", "ULUUN", "UNLU", "USAK", "VAKBN", "VAKFN",
    "VAKKO", "VANGD", "VBTYZ", "VERTU", "VERUS", "VESBE", "VESTL", "VKFYO", "VKGYO", "VKING",
    "YAPRK", "YAYLA", "YBTAS", "YEOTK", "YESIL", "YKBNK", "YKSL", "YUNSA", "YYAPI", "ZEDUR",
    "ZOREN", "ZRGYO"
])

bist_30 = [
    "AKBNK", "ALARK", "ASELS", "ASTOR", "BIMAS", "BRSAN", "EKGYO", "ENKAI", 
    "EREGL", "FROTO", "GARAN", "GESAN", "GUBRF", "HALKB", "HEKTS", "ISCTR", 
    "KCHOL", "KONTR", "KOZAA", "KOZAL", "KRDMD", "MGROS", "ODAS", "OYAKC", 
    "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TCELL", "THYAO", "TOASO", 
    "TUPRS", "VAKBN", "YKBNK", "ZOREN"
]

alternatif_varliklar = [
    "USD/TRY",
    "EUR/TRY",
    "GBP/TRY",
    "Gram Altın (TL)",
    "Gram Gümüş (TL)",
]
tum_islem_varliklari = sorted(bist_hisseler) + alternatif_varliklar

bitis_tarihi = datetime.datetime.now(TZ_TR).strftime("%d-%m-%Y")
baslangic_tarihi = (
    datetime.datetime.now(TZ_TR) - datetime.timedelta(days=365)
).strftime("%d-%m-%Y")

def motor_hisse_anlik_fiyat(hisse):
    try:
        yf_data = yf.Ticker(f"{hisse}.IS").history(period="1d")
        if not yf_data.empty:
            return float(yf_data["Close"].iloc[-1])
    except:
        pass
    return None

@st.cache_data(ttl=300)
def veri_cek_ve_hazirla(hisse):
  try:
    df = fetch_stock_data(
        symbols=[hisse], start_date=baslangic_tarihi, end_date=bitis_tarihi
    )
    if df is not None and not df.empty:
      df.columns = [str(col).upper() for col in df.columns]
      tarih_kolonu = next((c for c in df.columns if "TARIH" in c or "DATE" in c), None)
      kapanis_kolonu = next((c for c in df.columns if "KAP" in c or "CLOSE" in c or "FIYAT" in c), None)

      if tarih_kolonu and kapanis_kolonu:
        df["Tarih"] = pd.to_datetime(df[tarih_kolonu], format="%d-%m-%Y", errors="coerce")
        df = df.dropna(subset=["Tarih"]).sort_values("Tarih")
        df["Kapanis"] = pd.to_numeric(df[kapanis_kolonu], errors="coerce")
        
        try:
            yf_data = yf.Ticker(f"{hisse}.IS").history(period="1d")
            if not yf_data.empty:
                anlik_fiyat = float(yf_data["Close"].iloc[-1])
                bugun = pd.to_datetime(datetime.datetime.now(TZ_TR).date())
                son_tarih = pd.to_datetime(df["Tarih"].iloc[-1]).normalize()
                if bugun > son_tarih:
                    yeni_satir = pd.DataFrame({"Tarih": [bugun], "Kapanis": [anlik_fiyat]})
                    df = pd.concat([df, yeni_satir], ignore_index=True)
                else:
                    df.loc[df.index[-1], "Kapanis"] = anlik_fiyat
        except:
            pass 
        return df
  except:
    pass
  return None

@st.cache_data(ttl=60)
def alternatif_fiyat_cek(varlik):
  try:
    if varlik == "USD/TRY": return float(yf.Ticker("USDTRY=X").history(period="1d")["Close"].iloc[-1])
    elif varlik == "EUR/TRY": return float(yf.Ticker("EURTRY=X").history(period="1d")["Close"].iloc[-1])
    elif varlik == "GBP/TRY": return float(yf.Ticker("GBPTRY=X").history(period="1d")["Close"].iloc[-1])
    elif varlik == "Gram Altın (TL)":
      return float((yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1] * yf.Ticker("USDTRY=X").history(period="1d")["Close"].iloc[-1]) / 31.1035)
    elif varlik == "Gram Gümüş (TL)":
      return float((yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1] * yf.Ticker("USDTRY=X").history(period="1d")["Close"].iloc[-1]) / 31.1035)
  except:
    return 10.0
  return 10.0

@st.cache_data(ttl=1800)
def haberleri_ve_kap_getir(hisse_kodu):
  try:
    url_haber = f"https://news.google.com/rss/search?q={hisse_kodu}+hisse+borsa&hl=TR&gl=TR&ceid=TR:tr"
    haberler = [{"baslik": entry.title, "link": entry.link} for entry in parse(url_haber).entries[:4]]
    url_kap = f"https://news.google.com/rss/search?q={hisse_kodu}+KAP+bildirimi+özel+durum&hl=TR&gl=TR&ceid=TR:tr"
    kap_bildirimleri = [{"baslik": entry.title, "link": entry.link} for entry in parse(url_kap).entries[:4]]
    return haberler, kap_bildirimleri
  except:
    return [], []

def akilli_analiz_hesapla(df, kap_bildirimleri, haberler):
  nedenler = []
  puan = 0
  son_fiyat = df["Kapanis"].iloc[-1]
  delta = df["Kapanis"].diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
  rs = gain / loss
  df["RSI"] = 100 - (100 / (1 + rs))
  son_rsi = df["RSI"].iloc[-1]

  df["SMA50"] = df["Kapanis"].rolling(window=50).mean()
  df["SMA200"] = df["Kapanis"].rolling(window=200).mean()
  son_sma50 = df["SMA50"].iloc[-1]
  son_sma200 = df["SMA200"].iloc[-1]

  ideal_alim = son_fiyat * 0.97
  ideal_satim = son_fiyat * 1.05

  if son_rsi < 35: puan += 2; nedenler.append(f"RSI aşırı satımda ({son_rsi:.1f}).")
  elif son_rsi > 65: puan -= 2; nedenler.append(f"RSI aşırı alımda ({son_rsi:.1f}).")
  else: nedenler.append(f"RSI nötr bölgede ({son_rsi:.1f}).")

  if son_fiyat > son_sma50: puan += 1; nedenler.append("Fiyat 50 günlük ortalamanın üzerinde.")
  else: puan -= 1; nedenler.append("Fiyat 50 günlük ortalamanın altında.")

  if son_fiyat > son_sma200: puan += 2; nedenler.append("Uzun vadeli ana trend pozitif.")
  else: puan -= 2; nedenler.append("Uzun vadeli ana trend baskı altında.")

  olumlu = ["sözleşme", "ihale", "kar", "rekor", "artış", "onay", "yatırım"]
  olumsuz = ["zarar", "ceza", "soruşturma", "dava", "borç", "düşüş"]
  haber_skoru = 0
  tarananlar = [k["baslik"].lower() for k in kap_bildirimleri] + [h["baslik"].lower() for h in haberler]
  for m in tarananlar:
    for o in olumlu:
      if o in m: haber_skoru += 1
    for ol in olumsuz:
      if ol in m: haber_skoru -= 1

  if haber_skoru > 0: puan += 2; nedenler.append(f"Haber akışı olumlu.")
  elif haber_skoru < 0: puan -= 2; nedenler.append(f"Haber akışı olumsuz.")
  else: nedenler.append("Haber akışı dengeli.")

  karar = "AL" if puan >= 3 else ("SAT" if puan <= -2 else "TUT")
  return karar, puan, nedenler, son_fiyat, son_rsi, son_sma50, son_sma200, ideal_alim, ideal_satim

def arsekten_verileri_yukle():
  varsayilan_kullanicilar = {
      "Devrim": {"nakit": 1000000.0, "portfoy_hareketleri": [], "gunluk_gecmis": [], "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date())},
      "Orhan": {"nakit": 1000000.0, "portfoy_hareketleri": [], "gunluk_gecmis": [], "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date())},
      "Ali Yiğit": {"nakit": 1000000.0, "portfoy_hareketleri": [], "gunluk_gecmis": [], "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date())},
  }
  try:
    response = requests.get(WEBHOOK_URL, timeout=30)
    if response.status_code == 200:
      try:
        veri = response.json()
      except:
        return varsayilan_kullanicilar
      if isinstance(veri, list) and len(veri) > 0:
        for islem in veri:
          kullanici = islem.get("kullanici", "Devrim")
          if kullanici not in varsayilan_kullanicilar:
            varsayilan_kullanicilar[kullanici] = {"nakit": 1000000.0, "portfoy_hareketleri": [], "gunluk_gecmis": [], "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date())}
          tutar = float(str(islem.get("toplam_tutar", 0)).replace(",", "."))
          fiyat = float(str(islem.get("fiyat", 0)).replace(",", "."))
          lot = int(float(str(islem.get("lot", 0)).replace(",", ".")))
          islem_turu = islem.get("islem_turu")

          varsayilan_kullanicilar[kullanici]["portfoy_hareketleri"].append({
              "Zaman": islem.get("zaman", ""), "Hisse": islem.get("hisse", ""), "Tip": islem_turu,
              "Miktar": lot, "Fiyat": fiyat, "Tutar": tutar,
          })
          if islem_turu == "ALIŞ": varsayilan_kullanicilar[kullanici]["nakit"] -= tutar
          elif islem_turu == "SATIŞ": varsayilan_kullanicilar[kullanici]["nakit"] += tutar
  except:
    pass
  return varsayilan_kullanicilar

if "kullanicilar" not in st.session_state:
  st.session_state.kullanicilar = arsekten_verileri_yukle()
if "zincir_emirler" not in st.session_state:
  st.session_state.zincir_emirler = {}

st.sidebar.header("👤 Yatırımcı Profili")
secilen_kullanici = st.sidebar.selectbox("Aktif Trader Seçin:", list(st.session_state.kullanicilar.keys()))

if secilen_kullanici not in st.session_state.zincir_emirler:
    st.session_state.zincir_emirler[secilen_kullanici] = []

with st.sidebar.form("yeni_profil_formu"):
  yeni_kullanici_adi = st.text_input("Veya Yeni Trader Ekle:")
  if st.form_submit_button("Profili Oluştur/Geç") and yeni_kullanici_adi.strip():
      temiz_ad = yeni_kullanici_adi.strip()
      if temiz_ad not in st.session_state.kullanicilar:
        st.session_state.kullanicilar[temiz_ad] = {"nakit": 1000000.0, "portfoy_hareketleri": [], "gunluk_gecmis": [], "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date())}
        st.session_state.zincir_emirler[temiz_ad] = []
        st.rerun()

aktif_profil = st.session_state.kullanicilar[secilen_kullanici]
bugun_str = str(datetime.datetime.now(TZ_TR).date())
if aktif_profil["son_hesap_tarihi"] != bugun_str:
  aktif_profil["nakit"] += aktif_profil["nakit"] * 0.0012
  aktif_profil["son_hesap_tarihi"] = bugun_str

st.sidebar.markdown("---")
st.sidebar.caption("⚡ **Powered by Devrim YILDIZ**")
st.sidebar.caption("ℹ️ *Bu uygulama sadece kişisel fon yönetimi ve takip içindir.*")

tab_tekli, tab_matris, tab_portfoy, tab_liderlik, tab_zincir = st.tabs([
    "📊 Tekli Hisse & Derin Analiz",
    "🌐 Tüm Piyasa Sinyal Matrisi (Tarama)",
    f"💼 Sanal Portföy, Radar & Geçmiş ({secilen_kullanici})",
    "🏆 Liderlik & Yatırımcılar Matrisi",
    "⚙️ Otomatik & Zincir Emirler"
])

with tab_tekli:
  default_index = bist_hisseler.index("THYAO") if "THYAO" in bist_hisseler else 0
  secilen_hisse = st.selectbox("Analiz Etmek İstediğiniz Hisse Senedini Seçin:", bist_hisseler, index=default_index)

  with st.spinner(f"{secilen_hisse} gün içi verileri ve haberleri yükleniyor..."):
    df = veri_cek_ve_hazirla(secilen_hisse)
    haberler, kap_bildirimleri = haberleri_ve_kap_getir(secilen_hisse)

  if df is not None and not df.empty and "Kapanis" in df.columns:
    karar, puan, nedenler, son_fiyat, son_rsi, son_sma50, son_sma200, ideal_alim, ideal_satim = akilli_analiz_hesapla(df, kap_bildirimleri, haberler)
    renk = "🟢" if karar == "AL" else ("🔴" if karar == "SAT" else "🟡")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Son İşlem Fiyatı", f"{son_fiyat:.2f} TL")
    col2.metric("RSI (14)", f"{son_rsi:.1f}")
    col3.metric("İdeal Alım (Destek)", f"{ideal_alim:.2f} TL")
    col4.metric("İdeal Satış (Direnç)", f"{ideal_satim:.2f} TL")

    st.markdown("---")
    st.subheader(f"🧠 Akıllı Karar Önerisi: {renk} **{karar}** (Puan: {puan})")
    with st.expander("🔍 Gerekçeler ve Detaylı Analiz", expanded=True):
      for n in nedenler:
        st.markdown(f"- {n}")
    st.markdown("---")

    st.subheader(f"{secilen_hisse} Fiyat Grafiği")
    st.line_chart(df.set_index("Tarih")[["Kapanis", "SMA50", "SMA200"]])
    
    st.markdown("---")
    st.subheader(f"📰 {secilen_hisse} Son Haberler & KAP Bildirimleri")
    col_haber, col_kap = st.columns(2)
    with col_haber:
      st.markdown("**Son Haberler**")
      if haberler:
        for h in haberler: st.markdown(f"- [{h['baslik']}]({h['link']})")
      else: st.info("Haber bulunamadı.")
    with col_kap:
      st.markdown("**Son KAP Bildirimleri**")
      if kap_bildirimleri:
        for k in kap_bildirimleri: st.markdown(f"- [{k['baslik']}]({k['link']})")
      else: st.info("KAP bildirimi bulunamadı.")
  else:
    st.warning("Yeterli veri alınamadı.")

with tab_matris:
  st.subheader("🌐 BİST Genel Tarama ve Sıralı Sinyal Matrisi")
  st.markdown("Sistemdeki tüm hisseler taranır; en güçlü alım kağıtlarına **AL 1, AL 2...** derecesi verilir.")
  
  tarama_kapsami = st.radio("Tarama Hızı & Kapsamı:", ["Sadece Popüler/İlk 50 Hisse (Çok Hızlı ⚡)", "Tüm BİST Hisseleri (Yavaş 🐢)"], horizontal=True)

  if st.button("🚀 Piyasayı Tara ve Sıralı Matrisi Oluştur"):
    matris_verileri = []
    hedef_liste = bist_hisseler[:50] if "50" in tarama_kapsami else bist_hisseler
    toplam = len(hedef_liste)
    progress_bar = st.progress(0)
    
    def tekil_tara(h_kodu):
        try:
            df_m = veri_cek_ve_hazirla(h_kodu)
            if df_m is not None and not df_m.empty and len(df_m) > 30:
                k_karar, k_puan, _, k_fiyat, k_rsi, _, _, k_alim, k_satim = akilli_analiz_hesapla(df_m, [], [])
                return {"Hisse": h_kodu, "Puan": k_puan, "HamKarar": k_karar, "Son Fiyat (TL)": k_fiyat, "RSI": k_rsi, "İdeal Alım": k_alim, "İdeal Satış": k_satim}
        except: pass
        return None

    tamamlanan = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        gelecek_islemler = {executor.submit(tekil_tara, h_kodu): h_kodu for h_kodu in hedef_liste}
        for future in concurrent.futures.as_completed(gelecek_islemler):
            sonuc = future.result()
            if sonuc: matris_verileri.append(sonuc)
            tamamlanan += 1
            progress_bar.progress(tamamlanan / toplam)

    if matris_verileri:
      df_sonuc = pd.DataFrame(matris_verileri)
      al_grubu = df_sonuc[df_sonuc["HamKarar"] == "AL"].sort_values(by="Puan", ascending=False).reset_index(drop=True)
      sat_grubu = df_sonuc[df_sonuc["HamKarar"] == "SAT"].sort_values(by="Puan", ascending=True).reset_index(drop=True)
      tut_grubu = df_sonuc[df_sonuc["HamKarar"] == "TUT"].sort_values(by="Puan", ascending=False).reset_index(drop=True)

      final_liste = []
      for idx, row in al_grubu.iterrows():
        row["Sinyal Derecesi"] = f"🟢 AL {idx+1}"; final_liste.append(row)
      for idx, row in sat_grubu.iterrows():
        row["Sinyal Derecesi"] = f"🔴 SAT {idx+1}"; final_liste.append(row)
      for idx, row in tut_grubu.iterrows():
        row["Sinyal Derecesi"] = f"🟡 TUT"; final_liste.append(row)

      df_final = pd.DataFrame(final_liste)
      df_final = df_final[["Sinyal Derecesi", "Hisse", "Son Fiyat (TL)", "RSI", "İdeal Alım", "İdeal Satış", "Puan"]]
      st.session_state.tarama_sonucu = df_final
      st.success("Tarama ve Dereceli Sıralama Tamamlandı!")
    else:
      st.warning("Tarama sırasında yeterli veri alınamadı.")

  if "tarama_sonucu" in st.session_state:
    df_gosterim = st.session_state.tarama_sonucu
    st.dataframe(df_gosterim.style.format({"Son Fiyat (TL)": "{:.2f} TL", "RSI": "{:.1f}", "İdeal Alım": "{:.2f} TL", "İdeal Satış": "{:.2f} TL"}), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader(f"⚡ Hızlı İşlem Paneli ({secilen_kullanici} - Bakiye: {aktif_profil['nakit']:,.2f} TL)")
    
    portfoy_durumu_hizli = {}
    for isl in aktif_profil["portfoy_hareketleri"]:
      hh = isl["Hisse"]
      if hh not in portfoy_durumu_hizli: portfoy_durumu_hizli[hh] = 0
      if isl["Tip"] == "ALIŞ": portfoy_durumu_hizli[hh] += isl["Miktar"]
      elif isl["Tip"] == "SATIŞ": portfoy_durumu_hizli[hh] -= isl["Miktar"]
    sahip_olunan_hisseler = [h for h, lot in portfoy_durumu_hizli.items() if lot > 0]

    h1, h2, h3, h4 = st.columns(4)
    with h2: hizli_tip = st.selectbox("İşlem Tipi", ["ALIŞ", "SATIŞ"], key="hizli_tip_full")
    with h1:
      if hizli_tip == "SATIŞ":
        hizli_hisse = st.selectbox("Hisse Seçin", sahip_olunan_hisseler if sahip_olunan_hisseler else ["Portföy Boş"], key="hizli_hisse_satis_full")
      else:
        hizli_hisse = st.selectbox("Hisse Seçin", df_gosterim["Hisse"].tolist(), key="hizli_hisse_alis_full")
    with h3: hizli_lot = st.number_input("Lot", min_value=1, value=1000, step=100, key="hizli_lot_full")
    with h4:
      f_val = float(df_gosterim[df_gosterim["Hisse"] == hizli_hisse]["Son Fiyat (TL)"].values[0]) if hizli_hisse in df_gosterim["Hisse"].values else 10.0
      hizli_fiyat = st.number_input("Fiyat", min_value=0.01, value=f_val, step=0.05, format="%.2f", key=f"hizli_fiy_full_{hizli_hisse}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Hızlı Emri Gerçekleştir ve Kaydet", use_container_width=True, key="hizli_btn_full"):
      if hizli_hisse == "Portföy Boş":
        st.error("❌ Satış yapabileceğiniz hisse yok!")
      else:
        tutar = hizli_lot * hizli_fiyat
        z_str = datetime.datetime.now(TZ_TR).strftime("%d.%m.%Y %H:%M:%S")
        if hizli_tip == "ALIŞ" and aktif_profil["nakit"] >= tutar:
          aktif_profil["nakit"] -= tutar
          aktif_profil["portfoy_hareketleri"].append({"Zaman": z_str, "Hisse": hizli_hisse, "Tip": "ALIŞ", "Miktar": hizli_lot, "Fiyat": hizli_fiyat, "Tutar": tutar})
          st.success("Alış başarılı!")
          st.rerun()
        elif hizli_tip == "SATIŞ" and portfoy_durumu_hizli.get(hizli_hisse, 0) >= hizli_lot:
          aktif_profil["nakit"] += tutar
          aktif_profil["portfoy_hareketleri"].append({"Zaman": z_str, "Hisse": hizli_hisse, "Tip": "SATIŞ", "Miktar": hizli_lot, "Fiyat": hizli_fiyat, "Tutar": tutar})
          st.success("Satış başarılı!")
          st.rerun()
        else:
          st.error("Bakiye veya lot yetersiz!")

with tab_portfoy:
  st.subheader(f"💼 Sanal Portföy, Akıllı Radar & Tarihsel Serüven ({secilen_kullanici})")
  st.markdown("Başlangıç sermayeniz **1.000.000 TL**'dir. Nakitleriniz günlük **%0,12 repo faizi** ile nemalanır.")

  portfoy_durumu = {}
  toplam_varlik_degeri = 0
  hisse_degeri_toplam = 0
  doviz_degeri_toplam = 0
  altin_gumus_degeri_toplam = 0

  for islem in aktif_profil["portfoy_hareketleri"]:
    h = islem["Hisse"]; tip = islem["Tip"]; lot = islem["Miktar"]; fiyat = islem["Fiyat"]
    if h not in portfoy_durumu: portfoy_durumu[h] = {"lot": 0, "maliyet_harcama": 0}
    if tip == "ALIŞ":
      portfoy_durumu[h]["lot"] += lot
      portfoy_durumu[h]["maliyet_harcama"] += lot * fiyat
    elif tip == "SATIŞ":
      portfoy_durumu[h]["lot"] -= lot
      if portfoy_durumu[h]["lot"] > 0:
        portfoy_durumu[h]["maliyet_harcama"] -= (portfoy_durumu[h]["maliyet_harcama"] * (lot / (portfoy_durumu[h]["lot"] + lot)))
      else: portfoy_durumu[h]["maliyet_harcama"] = 0

  aktif_pozisyonlar = []
  for h, veri in portfoy_durumu.items():
    if veri["lot"] > 0:
      gf = alternatif_fiyat_cek(h) if h in alternatif_varliklar else (motor_hisse_anlik_fiyat(h) or (veri["maliyet_harcama"] / veri["lot"]))
      pdegeri = veri["lot"] * gf
      maliyet = veri["maliyet_harcama"]
      k_z = pdegeri - maliyet
      k_z_y = (k_z / maliyet * 100) if maliyet > 0 else 0
      toplam_varlik_degeri += pdegeri

      if h in ["USD/TRY", "EUR/TRY", "GBP/TRY"]: doviz_degeri_toplam += pdegeri
      elif h in ["Gram Altın (TL)", "Gram Gümüş (TL)"]: altin_gumus_degeri_toplam += pdegeri
      else: hisse_degeri_toplam += pdegeri

      aktif_pozisyonlar.append({"Varlık / Hisse": h, "Net Miktar / Lot": veri["lot"], "Toplam Maliyet (TL)": maliyet, "Güncel Değer (TL)": pdegeri, "Kâr / Zarar (TL)": k_z, "Kâr / Zarar (%)": k_z_y})

  toplam_toplam = aktif_profil["nakit"] + toplam_varlik_degeri
  toplam_kar_zarar = toplam_toplam - 1000000.0
  toplam_kar_zarar_yuzde = (toplam_kar_zarar / 1000000.0) * 100

  bugun_tarih = str(datetime.datetime.now(TZ_TR).date())
  mevcut_gunluk = aktif_profil["gunluk_gecmis"]
  if not mevcut_gunluk or mevcut_gunluk[-1]["Tarih"] != bugun_tarih:
    mevcut_gunluk.append({"Tarih": bugun_tarih, "Toplam Varlık": toplam_toplam, "Nakit": aktif_profil["nakit"], "Hisse": hisse_degeri_toplam, "Döviz": doviz_degeri_toplam, "Altın & Gümüş": altin_gumus_degeri_toplam})
  else:
    mevcut_gunluk[-1]["Toplam Varlık"] = toplam_toplam
    mevcut_gunluk[-1]["Nakit"] = aktif_profil["nakit"]
    mevcut_gunluk[-1]["Hisse"] = hisse_degeri_toplam
    mevcut_gunluk[-1]["Döviz"] = doviz_degeri_toplam
    mevcut_gunluk[-1]["Altın & Gümüş"] = altin_gumus_degeri_toplam

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Toplam Varlık", f"{toplam_toplam:,.2f} TL")
  c2.metric("Nakit (Repo Nemalı)", f"{aktif_profil['nakit']:,.2f} TL")
  c3.metric("Varlıklar Değeri", f"{toplam_varlik_degeri:,.2f} TL")
  c4.metric("Toplam Kâr / Zarar", f"{toplam_kar_zarar:,.2f} TL", f"{toplam_kar_zarar_yuzde:.2f}%")

  st.markdown("---")

  col_grafik1, col_grafik2 = st.columns(2)
  with col_grafik1:
    st.subheader("📈 Tarihsel Varlık Eğrisi")
    if len(mevcut_gunluk) > 0:
      st.line_chart(pd.DataFrame(mevcut_gunluk).set_index("Tarih")[["Toplam Varlık"]])
  with col_grafik2:
    st.subheader("🥧 Varlık Sınıfı Kırılımı (TL)")
    kirilim_df = pd.DataFrame({"Varlık Sınıfı": ["Nakit / Repo", "BİST Hisseler", "Döviz", "Altın & Gümüş"], "Tutar (TL)": [aktif_profil["nakit"], hisse_degeri_toplam, doviz_degeri_toplam, altin_gumus_degeri_toplam]}).set_index("Varlık Sınıfı")
    st.bar_chart(kirilim_df)

  st.markdown("---")
  col_islem1, col_islem2 = st.columns(2)

  with col_islem1:
    st.subheader("📝 Manuel Emir Girişi")
    islem_tipi = st.selectbox("İşlem Tipi", ["ALIŞ", "SATIŞ"], key="islem_tipi_p_full")
    if islem_tipi == "SATIŞ":
      sahip_olunan_v = [h for h, veri in portfoy_durumu.items() if veri["lot"] > 0]
      islem_hisse = st.selectbox("Varlık Seçin", sahip_olunan_v if sahip_olunan_v else ["Portföy Boş"], key="islem_hisse_s_full")
    else:
      islem_hisse = st.selectbox("Varlık Seçin", tum_islem_varliklari, key="islem_hisse_a_full")

    otomatik_fiyat = (alternatif_fiyat_cek(islem_hisse) if islem_hisse in alternatif_varliklar else (motor_hisse_anlik_fiyat(islem_hisse) or 10.0)) if islem_hisse != "Portföy Boş" else 10.0
    islem_miktar = st.number_input("Lot", min_value=1, value=1000, step=100, key=f"mik_full_{islem_hisse}")
    islem_fiyat = st.number_input("Fiyat", min_value=0.01, value=float(otomatik_fiyat), step=0.05, format="%.2f", key=f"fiy_full_{islem_hisse}")

    if st.button("Emri Gerçekleştir ve Kaydet", use_container_width=True, key="btn_exec_full"):
      if islem_hisse == "Portföy Boş":
        st.error("❌ Satış yapabileceğiniz varlık yok!")
      else:
        tutar = islem_miktar * islem_fiyat
        z_str = datetime.datetime.now(TZ_TR).strftime("%d.%m.%Y %H:%M:%S")
        if islem_tipi == "ALIŞ" and aktif_profil["nakit"] >= tutar:
          aktif_profil["nakit"] -= tutar
          aktif_profil["portfoy_hareketleri"].append({"Zaman": z_str, "Hisse": islem_hisse, "Tip": "ALIŞ", "Miktar": islem_miktar, "Fiyat": islem_fiyat, "Tutar": tutar})
          st.success("Alış başarılı!")
          st.rerun()
        elif islem_tipi == "SATIŞ" and portfoy_durumu.get(islem_hisse, {}).get("lot", 0) >= islem_miktar:
          aktif_profil["nakit"] += tutar
          aktif_profil["portfoy_hareketleri"].append({"Zaman": z_str, "Hisse": islem_hisse, "Tip": "SATIŞ", "Miktar": islem_miktar, "Fiyat": islem_fiyat, "Tutar": tutar})
          st.success("Satış başarılı!")
          st.rerun()
        else:
          st.error("Yetersiz bakiye veya lot!")

  with col_islem2:
    st.subheader("📊 Aktif Varlık Dağılımınız")
    if aktif_pozisyonlar:
      st.dataframe(pd.DataFrame(aktif_pozisyonlar).style.format({"Net Miktar / Lot": "{:,}", "Toplam Maliyet (TL)": "{:,.2f} TL", "Güncel Değer (TL)": "{:,.2f} TL", "Kâr / Zarar (TL)": "{:,.2f} TL", "Kâr / Zarar (%)": "{:.2f}%"}), use_container_width=True, hide_index=True)
    else:
      st.info("Portföyünüzde aktif varlık yok.")

  st.markdown("---")
  st.subheader("📜 Geçmiş İşlem Günlüğünüz")
  if aktif_profil["portfoy_hareketleri"]:
    st.dataframe(pd.DataFrame(aktif_profil["portfoy_hareketleri"]).style.format({"Miktar": "{:,}", "Fiyat": "{:.2f} TL", "Tutar": "{:,.2f} TL"}), use_container_width=True, hide_index=True)

  if st.button("🔄 Portföyü Sıfırla"):
    st.session_state.kullanicilar[secilen_kullanici] = {"nakit": 1000000.0, "portfoy_hareketleri": [], "gunluk_gecmis": [], "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date())}
    st.rerun()

with tab_liderlik:
  st.subheader("🏆 Yatırımcılar Liderlik Matrisi")
  liderlik = []
  for k_adi, prof in st.session_state.kullanicilar.items():
    liderlik.append({"Trader": k_adi, "Nakit": prof["nakit"]})
  st.dataframe(pd.DataFrame(liderlik), use_container_width=True)


# --- 5. SEKME: OTOMATİK & ZİNCİR EMİRLER (DİNAMİK FİYAT MİMARİSİ) ---
with tab_zincir:
  st.subheader("⚙️ Otomatik Alım-Satım & Zincir Emir Modülü")
  st.markdown("Bu ekrandan hedef fiyatlar belirleyerek birbirine bağlı 10 slotlu zincir emirler kurabilirsiniz.")

  col_motor, col_bilgi = st.columns([1, 2])
  with col_motor:
      motor_aktif = st.toggle("🚀 Emir Motorunu Başlat (Sürekli Tarama)", value=False)
  with col_bilgi:
      if motor_aktif: st.success("Motor devrede! Fiyatlar taranıyor...")
      else: st.info("Motor kapalı.")

  st.markdown("---")
  st.subheader("🔗 Yeni Emir & Zincir Senaryosu Kur")
  
  portfoy_durumu_z = {}
  for islem in aktif_profil["portfoy_hareketleri"]:
    h, tip, lot, fiyat = islem["Hisse"], islem["Tip"], islem["Miktar"], islem["Fiyat"]
    if h not in portfoy_durumu_z: portfoy_durumu_z[h] = {"lot": 0, "toplam_maliyet": 0}
    if tip == "ALIŞ":
      portfoy_durumu_z[h]["lot"] += lot
      portfoy_durumu_z[h]["toplam_maliyet"] += lot * fiyat
    elif tip == "SATIŞ":
      portfoy_durumu_z[h]["lot"] -= lot

  portfoy_secenekleri = []
  for h, v in portfoy_durumu_z.items():
      if v["lot"] > 0:
          birim_maliyet = v["toplam_maliyet"] / v["lot"]
          portfoy_secenekleri.append(f"{h} (Portföyde: {v['lot']:,} Lot | Maliyet: {birim_maliyet:.2f} TL)")

  with st.form("zincir_kurulum_formu"):
      st.markdown("**1. Adım: Ana Tetikleyici Emir**")
      col_m1, col_m2, col_m3, col_m4 = st.columns(4)
      
      z_tip = col_m2.selectbox("İşlem Tipi", ["SATIŞ", "ALIŞ"], key="z_tip_dyn")

      if z_tip == "SATIŞ":
          satis_havuzu = []
          if portfoy_secenekleri: satis_havuzu.extend(portfoy_secenekleri)
          satis_havuzu.append("--- BİST 30 HİSSELERİ (Açığa Satış Opsiyonu) ---")
          satis_havuzu.extend(bist_30)
          
          secilen_ham_veri = col_m1.selectbox("Hisse / Varlık", satis_havuzu, key="z_hisse_s_dyn")
          z_hisse = secilen_ham_veri.split(" ")[0] if "---" not in secilen_ham_veri else "THYAO"
      else:
          z_hisse = col_m1.selectbox("Hisse / Varlık", tum_islem_varliklari, key="z_hisse_a_dyn")

      # --- DİNAMİK FİYAT HESAPLAMA (Hedef fiyatın hissenin gerçek değerine yakın gelmesi için) ---
      if z_hisse != "---":
          if z_hisse in alternatif_varliklar:
              baz_fiyat = alternatif_fiyat_cek(z_hisse)
          else:
              baz_fiyat = motor_hisse_anlik_fiyat(z_hisse) or 50.0
      else:
          baz_fiyat = 10.0

      z_fiyat = col_m3.number_input("Hedef Fiyat (TL)", min_value=0.01, value=float(baz_fiyat), step=0.05, format="%.2f", key=f"z_fiyat_dyn_{z_hisse}")
      z_lot = col_m4.number_input("Miktar (Lot)", min_value=1, value=100, step=10, key="z_lot_dyn")

      st.markdown("**2. Adım: Zincir Halka Emirler (10 Slot)**")
      zincir_adimlari = []
      for i in range(1, 11):
          with st.expander(f"Zincir Adım {i} (Opsiyonel)"):
              zc1, zc2, zc3 = st.columns(3)
              zincir_tip = zc1.selectbox(f"{i}. Tip", ["SATIŞ", "ALIŞ"], key=f"ztip_dyn_{i}")
              zincir_fiyat = zc2.number_input(f"{i}. Hedef Fiyat", min_value=0.0, value=0.0, step=0.05, key=f"zfiy_dyn_{i}")
              zincir_lot = zc3.number_input(f"{i}. Miktar", min_value=0, value=0, step=10, key=f"zlot_dyn_{i}")
              zincir_adimlari.append({"adim": i, "tip": zincir_tip, "fiyat": zincir_fiyat, "lot": zincir_lot})

      if st.form_submit_button("✅ Emir Senaryosunu Sisteme Yükle"):
          if z_hisse != "---":
              ana_emir_id = str(uuid.uuid4())[:8]
              st.session_state.zincir_emirler[secilen_kullanici].append({"id": ana_emir_id, "bagli_id": None, "hisse": z_hisse, "tip": z_tip, "fiyat": z_fiyat, "lot": z_lot, "durum": "BEKLİYOR"})
              onceki_id = ana_emir_id
              eklenen = 0
              for adim in zincir_adimlari:
                  if adim["fiyat"] > 0 and adim["lot"] > 0:
                      yeni_id = str(uuid.uuid4())[:8]
                      st.session_state.zincir_emirler[secilen_kullanici].append({"id": yeni_id, "bagli_id": onceki_id, "hisse": z_hisse, "tip": adim["tip"], "fiyat": adim["fiyat"], "lot": adim["lot"], "durum": "PASİF (Önceki Bekleniyor)"})
                      onceki_id = yeni_id; eklenen += 1
              st.success(f"Ana emir ve {eklenen} adet zincir adım başarıyla yüklendi!")
              st.rerun()

  st.markdown("---")
  st.subheader("📋 Bekleyen Emirler")
  kullanici_emirleri = st.session_state.zincir_emirler[secilen_kullanici]
  if kullanici_emirleri:
      st.dataframe(pd.DataFrame(kullanici_emirleri), use_container_width=True)
      if st.button("🗑️ Tamamlananları Temizle", key="temizle_zincir_dyn"):
          st.session_state.zincir_emirler[secilen_kullanici] = [e for e in kullanici_emirleri if e["durum"] in ["BEKLİYOR", "PASİF (Önceki Bekleniyor)"]]
          st.rerun()
  else:
      st.info("Bekleyen emir yok.")

  if motor_aktif:
      z_str = datetime.datetime.now(TZ_TR).strftime("%d.%m.%Y %H:%M:%S")
      def emir_gerceklesti_mi(hedef_id):
          return any(e["id"] == hedef_id and e["durum"] == "GERÇEKLEŞTİ" for e in kullanici_emirleri)

      for emir in kullanici_emirleri:
          if emir["durum"] == "PASİF (Önceki Bekleniyor)" and emir_gerceklesti_mi(emir["bagli_id"]):
              emir["durum"] = "BEKLİYOR"
          if emir["durum"] == "BEKLİYOR":
              anlik_f = alternatif_fiyat_cek(emir["hisse"]) if emir["hisse"] in alternatif_varliklar else motor_hisse_anlik_fiyat(emir["hisse"])
              if anlik_f:
                  ttutar = emir["lot"] * anlik_f
                  tetik = False
                  if emir["tip"] == "ALIŞ" and anlik_f <= emir["fiyat"] and aktif_profil["nakit"] >= ttutar:
                      aktif_profil["nakit"] -= ttutar; tetik = True
                  elif emir["tip"] == "SATIŞ" and anlik_f >= emir["fiyat"]:
                      aktif_profil["nakit"] += ttutar; tetik = True
                  if tetik:
                      aktif_profil["portfoy_hareketleri"].append({"Zaman": z_str, "Hisse": emir["hisse"], "Tip": emir["tip"], "Miktar": emir["lot"], "Fiyat": anlik_f, "Tutar": ttutar})
                      emir["durum"] = "GERÇEKLEŞTİ"
                      try:
                          requests.post(WEBHOOK_URL, json={"zaman": z_str, "kullanici": secilen_kullanici, "hisse": emir["hisse"], "islem_turu": emir["tip"], "lot": emir["lot"], "fiyat": anlik_f, "toplam_tutar": ttutar}, timeout=5)
                      except: pass
      time.sleep(30)
      st.rerun()
