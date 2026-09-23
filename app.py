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
    " Sanal Portföy, Hızlı İşlem Paneli ve **Otomatik Zincir Emir Motoru**."
)

# GARANTİLİ WEBHOOK URL'NİZ
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz8Z6yiVGpGTmg2k3I3htQrkxVrKFpZFNeP7qjxxDS8mzrQ1B6LrTJ67q4Dokkh667LnQ/exec"

# BİST TÜM Hisseleri
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

alternatif_varliklar = ["USD/TRY", "EUR/TRY", "GBP/TRY", "Gram Altın (TL)", "Gram Gümüş (TL)"]
tum_islem_varliklari = sorted(bist_hisseler) + alternatif_varliklar

bitis_tarihi = datetime.datetime.now(TZ_TR).strftime("%d-%m-%Y")
baslangic_tarihi = (datetime.datetime.now(TZ_TR) - datetime.timedelta(days=365)).strftime("%d-%m-%Y")

# --- HIZLI ANLIK FİYAT ÇEKİCİ (MOTOR İÇİN) ---
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
    df = fetch_stock_data(symbols=[hisse], start_date=baslangic_tarihi, end_date=bitis_tarihi)
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
    elif varlik == "Gram Altın (TL)": return float((yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1] * yf.Ticker("USDTRY=X").history(period="1d")["Close"].iloc[-1]) / 31.1035)
    elif varlik == "Gram Gümüş (TL)": return float((yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1] * yf.Ticker("USDTRY=X").history(period="1d")["Close"].iloc[-1]) / 31.1035)
  except: return 10.0
  return 10.0

@st.cache_data(ttl=1800)
def haberleri_ve_kap_getir(hisse_kodu):
  try:
    url_haber = f"https://news.google.com/rss/search?q={hisse_kodu}+hisse+borsa&hl=TR&gl=TR&ceid=TR:tr"
    haberler = [{"baslik": entry.title, "link": entry.link} for entry in parse(url_haber).entries[:4]]
    url_kap = f"https://news.google.com/rss/search?q={hisse_kodu}+KAP+bildirimi+özel+durum&hl=TR&gl=TR&ceid=TR:tr"
    kap_bildirimleri = [{"baslik": entry.title, "link": entry.link} for entry in parse(url_kap).entries[:4]]
    return haberler, kap_bildirimleri
  except: return [], []

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

  if haber_skoru > 0: puan += 2
  elif haber_skoru < 0: puan -= 2

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
      except Exception:
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
st.sidebar.caption("ℹ️ *Bu uygulama sadece kişisel fon yönetimi ve takip içindir. Yatırım tavsiyesi içermez.*")

# YENİ SEKME YAPISI: Otomatik & Zincir Emirler Eklendi
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
      for n in nedenler: st.markdown(f"- {n}")
    st.markdown("---")
    st.subheader(f"{secilen_hisse} Fiyat Grafiği")
    st.line_chart(df.set_index("Tarih")[["Kapanis", "SMA50", "SMA200"]])
  else:
    st.warning("Yeterli veri alınamadı.")

with tab_matris:
  st.subheader("🌐 BİST Genel Tarama ve Sıralı Sinyal Matrisi")
  tarama_kapsami = st.radio("Tarama Hızı:", ["Sadece Popüler/İlk 50 Hisse (Çok Hızlı ⚡)", "Tüm BİST Hisseleri (Yavaş 🐢)"], horizontal=True)
  if st.button("🚀 Piyasayı Tara ve Sıralı Matrisi Oluştur"):
    matris_verileri = []
    hedef_liste = bist_hisseler[:50] if "50" in tarama_kapsami else bist_hisseler
    progress_bar = st.progress(0)
    def tekil_tara(h_kodu):
        try:
            df_m = veri_cek_ve_hazirla(h_kodu)
            if df_m is not None and len(df_m) > 30:
                k_karar, k_puan, _, k_fiyat, k_rsi, _, _, k_alim, k_satim = akilli_analiz_hesapla(df_m, [], [])
                return {"Hisse": h_kodu, "Puan": k_puan, "HamKarar": k_karar, "Son Fiyat (TL)": k_fiyat, "RSI": k_rsi, "İdeal Alım": k_alim, "İdeal Satış": k_satim}
        except: pass
        return None
    tamamlanan = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        gelecek = {executor.submit(tekil_tara, h): h for h in hedef_liste}
        for future in concurrent.futures.as_completed(gelecek):
            if future.result(): matris_verileri.append(future.result())
            tamamlanan += 1
            progress_bar.progress(tamamlanan / len(hedef_liste))
    if matris_verileri:
      df_sonuc = pd.DataFrame(matris_verileri)
      df_sonuc["Sinyal Derecesi"] = df_sonuc.apply(lambda r: f"🟢 AL" if r.HamKarar=="AL" else (f"🔴 SAT" if r.HamKarar=="SAT" else "🟡 TUT"), axis=1)
      st.session_state.tarama_sonucu = df_sonuc.sort_values(by=["HamKarar", "Puan"], ascending=[True, False])
      st.success("Tarama Tamamlandı!")

  if "tarama_sonucu" in st.session_state:
    st.dataframe(st.session_state.tarama_sonucu[["Sinyal Derecesi", "Hisse", "Son Fiyat (TL)", "RSI", "Puan"]], use_container_width=True, hide_index=True)

with tab_portfoy:
  st.subheader(f"💼 Sanal Portföy ({secilen_kullanici})")
  portfoy_durumu = {}
  toplam_varlik_degeri = 0
  for islem in aktif_profil["portfoy_hareketleri"]:
    h, tip, lot, fiyat = islem["Hisse"], islem["Tip"], islem["Miktar"], islem["Fiyat"]
    if h not in portfoy_durumu: portfoy_durumu[h] = {"lot": 0, "maliyet": 0}
    if tip == "ALIŞ":
      portfoy_durumu[h]["lot"] += lot
      portfoy_durumu[h]["maliyet"] += lot * fiyat
    elif tip == "SATIŞ":
      portfoy_durumu[h]["lot"] -= lot
      if portfoy_durumu[h]["lot"] > 0: portfoy_durumu[h]["maliyet"] -= (portfoy_durumu[h]["maliyet"] * (lot / (portfoy_durumu[h]["lot"] + lot)))
      else: portfoy_durumu[h]["maliyet"] = 0

  aktif_pozisyonlar = []
  for h, veri in portfoy_durumu.items():
    if veri["lot"] > 0:
      guncel_fiyat = alternatif_fiyat_cek(h) if h in alternatif_varliklar else motor_hisse_anlik_fiyat(h)
      if not guncel_fiyat: guncel_fiyat = veri["maliyet"] / veri["lot"]
      piyasa_degeri = veri["lot"] * guncel_fiyat
      toplam_varlik_degeri += piyasa_degeri
      aktif_pozisyonlar.append({"Varlık": h, "Lot": veri["lot"], "Maliyet": veri["maliyet"], "Güncel Değer": piyasa_degeri, "K/Z": piyasa_degeri - veri["maliyet"]})

  toplam_toplam = aktif_profil["nakit"] + toplam_varlik_degeri
  c1, c2, c3 = st.columns(3)
  c1.metric("Toplam Varlık", f"{toplam_toplam:,.2f} TL")
  c2.metric("Nakit Bakiye", f"{aktif_profil['nakit']:,.2f} TL")
  c3.metric("K/Z Durumu", f"{toplam_toplam - 1000000:,.2f} TL")

  if aktif_pozisyonlar:
    st.dataframe(pd.DataFrame(aktif_pozisyonlar).style.format({"Lot": "{:,}", "Maliyet": "{:,.2f}", "Güncel Değer": "{:,.2f}", "K/Z": "{:,.2f}"}), use_container_width=True)

with tab_liderlik:
  st.subheader("🏆 Liderlik Matrisi")
  liderlik_verileri = []
  for k_adi, prof in st.session_state.kullanicilar.items():
      liderlik_verileri.append({"Trader": k_adi, "Nakit": prof["nakit"]})
  st.dataframe(pd.DataFrame(liderlik_verileri), use_container_width=True)


# --- 5. SEKME: OTOMATİK VE ZİNCİR EMİRLER ---
with tab_zincir:
  st.subheader("⚙️ Otomatik Alım-Satım & Zincir Emir Modülü")
  st.markdown("Bu ekrandan hedef fiyatları belirleyerek tekli veya **birbirine bağlı zincir emirler** kurabilirsiniz. Tetikleyici Motor açık olduğu sürece sistem piyasayı otomatik tarar ve şartlar oluştuğunda işlemleri gerçekleştirir.")

  col_motor, col_bilgi = st.columns([1, 2])
  with col_motor:
      # SADECE BU BUTON AÇIKKEN OTOMATİK TARAMA YAPAR
      motor_aktif = st.toggle("🚀 Emir Motorunu Başlat (Sürekli Tarama)", value=False)
  with col_bilgi:
      if motor_aktif:
          st.success("Tetikleyici Motor Devrede! Sistem her 30 saniyede bir güncel fiyatları tarayarak şartlı emirleri kontrol ediyor...")
      else:
          st.info("Motor kapalı. Bekleyen emirleriniz kayıtlı duruyor ancak piyasa izlenmiyor.")

  st.markdown("---")
  st.subheader("🔗 Yeni Emir & Zincir Senaryosu Kur")
  
  with st.form("zincir_kurulum_formu"):
      st.markdown("**1. Adım: Ana Tetikleyici Emir** (İlk bu şartın gerçekleşmesi beklenir)")
      col_m1, col_m2, col_m3, col_m4 = st.columns(4)
      z_hisse = col_m1.selectbox("Hisse / Varlık", tum_islem_varliklari)
      z_tip = col_m2.selectbox("İşlem Tipi", ["ALIŞ", "SATIŞ"])
      z_fiyat = col_m3.number_input("Hedef Fiyat (TL)", min_value=0.01, value=10.0, step=0.05)
      z_lot = col_m4.number_input("Miktar (Lot)", min_value=1, value=100, step=10)

      st.markdown("**2. Adım: Zincir Halka Emirler** (Ana emir gerçekleşirse sırayla aktif olurlar. İstemiyorsanız 0 bırakın)")
      
      zincir_adimlari = []
      # 10 Slot Zincir Döngüsü
      for i in range(1, 11):
          with st.expander(f"Zincir Adım {i} (Opsiyonel)"):
              zc1, zc2, zc3 = st.columns(3)
              zincir_tip = zc1.selectbox(f"{i}. Tip", ["ALIŞ", "SATIŞ"], key=f"ztip_{i}")
              zincir_fiyat = zc2.number_input(f"{i}. Hedef Fiyat", min_value=0.0, value=0.0, step=0.05, key=f"zfiy_{i}")
              zincir_lot = zc3.number_input(f"{i}. Miktar", min_value=0, value=0, step=10, key=f"zlot_{i}")
              zincir_adimlari.append({
                  "adim": i, "tip": zincir_tip, "fiyat": zincir_fiyat, "lot": zincir_lot
              })

      z_kaydet = st.form_submit_button("✅ Emir Senaryosunu Sisteme Yükle")
      if z_kaydet:
          ana_emir_id = str(uuid.uuid4())[:8]
          
          # Ana Emri Ekle
          st.session_state.zincir_emirler[secilen_kullanici].append({
              "id": ana_emir_id,
              "bagli_id": None,
              "hisse": z_hisse,
              "tip": z_tip,
              "fiyat": z_fiyat,
              "lot": z_lot,
              "durum": "BEKLİYOR"
          })
          
          # Geçerli Zincir Emirleri Ekle (Fiyat ve Lot 0'dan büyükse)
          onceki_id = ana_emir_id
          eklenen_zincir_sayisi = 0
          for adim in zincir_adimlari:
              if adim["fiyat"] > 0 and adim["lot"] > 0:
                  yeni_id = str(uuid.uuid4())[:8]
                  st.session_state.zincir_emirler[secilen_kullanici].append({
                      "id": yeni_id,
                      "bagli_id": onceki_id,
                      "hisse": z_hisse,
                      "tip": adim["tip"],
                      "fiyat": adim["fiyat"],
                      "lot": adim["lot"],
                      "durum": "PASİF (Önceki Bekleniyor)"
                  })
                  onceki_id = yeni_id
                  eklenen_zincir_sayisi += 1
                  
          st.success(f"Ana emir ve {eklenen_zincir_sayisi} adet zincir adım başarıyla havuza eklendi!")
          st.rerun()

  st.markdown("---")
  st.subheader("📋 Bekleyen ve Gerçekleşen Emir Havuzu")
  
  kullanici_emirleri = st.session_state.zincir_emirler[secilen_kullanici]
  if kullanici_emirleri:
      df_emirler = pd.DataFrame(kullanici_emirleri)
      st.dataframe(df_emirler, use_container_width=True)
      if st.button("🗑️ Gerçekleşenleri ve İptalleri Temizle"):
          st.session_state.zincir_emirler[secilen_kullanici] = [e for e in kullanici_emirleri if e["durum"] in ["BEKLİYOR", "PASİF (Önceki Bekleniyor)"]]
          st.rerun()
  else:
      st.info("Şu an havuzunuzda bekleyen hiçbir otomatik/şartlı emir yok.")

  # ==========================================
  # TETİKLEYİCİ MOTOR MANTIĞI (AUTO-REFRESH)
  # ==========================================
  if motor_aktif:
      islem_oldu_mu = False
      zaman_str = datetime.datetime.now(TZ_TR).strftime("%d.%m.%Y %H:%M:%S")
      
      def emir_gerceklesti_mi(hedef_id):
          for e in kullanici_emirleri:
              if e["id"] == hedef_id and e["durum"] == "GERÇEKLEŞTİ":
                  return True
          return False

      for emir in kullanici_emirleri:
          # Eğer emir Pasifse ve bağlı olduğu üst emir gerçekleşmişse onu Bekliyor'a çek
          if emir["durum"] == "PASİF (Önceki Bekleniyor)":
              if emir_gerceklesti_mi(emir["bagli_id"]):
                  emir["durum"] = "BEKLİYOR"
                  islem_oldu_mu = True

          # Eğer emir BEKLİYOR aşamasındaysa piyasaya bak
          if emir["durum"] == "BEKLİYOR":
              # Canlı fiyatı çek
              if emir["hisse"] in alternatif_varliklar:
                  anlik_f = alternatif_fiyat_cek(emir["hisse"])
              else:
                  anlik_f = motor_hisse_anlik_fiyat(emir["hisse"])
              
              if anlik_f:
                  toplam_tutar = emir["lot"] * anlik_f
                  tetiklendi = False
                  
                  if emir["tip"] == "ALIŞ" and anlik_f <= emir["fiyat"]:
                      if aktif_profil["nakit"] >= toplam_tutar:
                          aktif_profil["nakit"] -= toplam_tutar
                          tetiklendi = True
                      else:
                          emir["durum"] = "İPTAL (Yetersiz Nakit)"
                          islem_oldu_mu = True
                          
                  elif emir["tip"] == "SATIŞ" and anlik_f >= emir["fiyat"]:
                      # Portföydeki lotu kontrol et
                      sahip_olunan = sum([i["Miktar"] for i in aktif_profil["portfoy_hareketleri"] if i["Hisse"] == emir["hisse"] and i["Tip"] == "ALIŞ"]) - \
                                     sum([i["Miktar"] for i in aktif_profil["portfoy_hareketleri"] if i["Hisse"] == emir["hisse"] and i["Tip"] == "SATIŞ"])
                      if sahip_olunan >= emir["lot"]:
                          aktif_profil["nakit"] += toplam_tutar
                          tetiklendi = True
                      else:
                          emir["durum"] = "İPTAL (Yetersiz Lot)"
                          islem_oldu_mu = True

                  # Şartlar uyduysa işlemi terminale ve E-Tabloya kaydet
                  if tetiklendi:
                      aktif_profil["portfoy_hareketleri"].append({
                          "Zaman": zaman_str, "Hisse": emir["hisse"], "Tip": emir["tip"],
                          "Miktar": emir["lot"], "Fiyat": anlik_f, "Tutar": toplam_tutar
                      })
                      emir["durum"] = "GERÇEKLEŞTİ"
                      islem_oldu_mu = True
                      try:
                          requests.post(WEBHOOK_URL, json={"zaman": zaman_str, "kullanici": secilen_kullanici, "hisse": emir["hisse"], "islem_turu": emir["tip"], "lot": emir["lot"], "fiyat": anlik_f, "toplam_tutar": toplam_tutar}, timeout=5)
                      except: pass

      # Motorun Streamlit arayüzünü kilitlememesi ve sürekli dönmesi için 30 saniye uyutup sayfayı yeniliyoruz.
      time.sleep(30)
      st.rerun()
