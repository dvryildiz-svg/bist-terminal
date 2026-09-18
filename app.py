import concurrent.futures
import datetime
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
    "Tüm BİST Hisseleri Evreni, Sıralı Sinyaller (AL1, SAT1...), Canlı Fiyat"
    " Entegrasyonu, Günlük Nemalandırma (%0,12), Sanal Portföy Akıllı Radarı,"
    " Çoklu Kullanıcı Liderlik Matrisi ve Hızlı İşlem Paneli."
)

# GARANTİLİ (İsme Göre Bulan) YENİ WEBHOOK URL'NİZ
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz8Z6yiVGpGTmg2k3I3htQrkxVrKFpZFNeP7qjxxDS8mzrQ1B6LrTJ67q4Dokkh667LnQ/exec"

# BİST TÜM ve Ana Pazar Hisselerinin Tam Kapsamlı Listesi
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

alternatif_varliklar = [
    "USD/TRY",
    "EUR/TRY",
    "GBP/TRY",
    "Gram Altın (TL)",
    "Gram Gümüş (TL)",
]
tum_islem_varliklari = sorted(bist_hisseler) + alternatif_varliklar

# Zamanları Türkiye saatine göre alıyoruz
bitis_tarihi = datetime.datetime.now(TZ_TR).strftime("%d-%m-%Y")
baslangic_tarihi = (
    datetime.datetime.now(TZ_TR) - datetime.timedelta(days=365)
).strftime("%d-%m-%Y")


@st.cache_data(ttl=3600)
def veri_cek_ve_hazirla(hisse):
  try:
    df = fetch_stock_data(
        symbols=[hisse], start_date=baslangic_tarihi, end_date=bitis_tarihi
    )
    if df is not None and not df.empty:
      df.columns = [str(col).upper() for col in df.columns]
      tarih_kolonu = next(
          (c for c in df.columns if "TARIH" in c or "DATE" in c), None
      )
      kapanis_kolonu = next(
          (
              c
              for c in df.columns
              if "KAP" in c or "CLOSE" in c or "FIYAT" in c
          ),
          None,
      )

      if tarih_kolonu and kapanis_kolonu:
        df["Tarih"] = pd.to_datetime(
            df[tarih_kolonu], format="%d-%m-%Y", errors="coerce"
        )
        df = df.dropna(subset=["Tarih"]).sort_values("Tarih")
        df["Kapanis"] = pd.to_numeric(df[kapanis_kolonu], errors="coerce")
        return df
  except:
    pass
  return None


@st.cache_data(ttl=60)
def alternatif_fiyat_cek(varlik):
  try:
    if varlik == "USD/TRY":
      t = yf.Ticker("USDTRY=X")
      return float(t.history(period="1d")["Close"].iloc[-1])
    elif varlik == "EUR/TRY":
      t = yf.Ticker("EURTRY=X")
      return float(t.history(period="1d")["Close"].iloc[-1])
    elif varlik == "GBP/TRY":
      t = yf.Ticker("GBPTRY=X")
      return float(t.history(period="1d")["Close"].iloc[-1])
    elif varlik == "Gram Altın (TL)":
      altin_ons = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
      usd_try = yf.Ticker("USDTRY=X").history(period="1d")["Close"].iloc[-1]
      return float((altin_ons * usd_try) / 31.1035)
    elif varlik == "Gram Gümüş (TL)":
      gumus_ons = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]
      usd_try = yf.Ticker("USDTRY=X").history(period="1d")["Close"].iloc[-1]
      return float((gumus_ons * usd_try) / 31.1035)
  except:
    return 10.0
  return 10.0


@st.cache_data(ttl=1800)
def haberleri_ve_kap_getir(hisse_kodu):
  try:
    url_haber = f"https://news.google.com/rss/search?q={hisse_kodu}+hisse+borsa&hl=TR&gl=TR&ceid=TR:tr"
    feed_haber = parse(url_haber)
    haberler = [
        {
            "baslik": entry.title,
            "link": entry.link,
            "zaman": getattr(entry, "published", "Güncel"),
        }
        for entry in feed_haber.entries[:4]
    ]

    url_kap = f"https://news.google.com/rss/search?q={hisse_kodu}+KAP+bildirimi+özel+durum&hl=TR&gl=TR&ceid=TR:tr"
    feed_kap = parse(url_kap)
    kap_bildirimleri = [
        {
            "baslik": entry.title,
            "link": entry.link,
            "zaman": getattr(entry, "published", "Güncel"),
        }
        for entry in feed_kap.entries[:4]
    ]

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

  if son_rsi < 35:
    puan += 2
    nedenler.append(
        f"RSI aşırı satımda ({son_rsi:.1f}), tepki alımı gelebilir."
    )
  elif son_rsi > 65:
    puan -= 2
    nedenler.append(f"RSI aşırı alımda ({son_rsi:.1f}), dikkatli olunmalı.")
  else:
    nedenler.append(f"RSI nötr bölgede ({son_rsi:.1f}).")

  if son_fiyat > son_sma50:
    puan += 1
    nedenler.append("Fiyat 50 günlük ortalamanın üzerinde.")
  else:
    puan -= 1
    nedenler.append("Fiyat 50 günlük ortalamanın altında.")

  if son_fiyat > son_sma200:
    puan += 2
    nedenler.append("Uzun vadeli ana trend pozitif.")
  else:
    puan -= 2
    nedenler.append("Uzun vadeli ana trend baskı altında.")

  olumlu = ["sözleşme", "ihale", "kar", "rekor", "artış", "onay", "yatırım"]
  olumsuz = ["zarar", "ceza", "soruşturma", "dava", "borç", "düşüş"]
  haber_skoru = 0
  tarananlar = [k["baslik"].lower() for k in kap_bildirimleri] + [
      h["baslik"].lower() for h in haberler
  ]
  for m in tarananlar:
    for o in olumlu:
      if o in m:
        haber_skoru += 1
    for ol in olumsuz:
      if ol in m:
        haber_skoru -= 1

  if haber_skoru > 0:
    puan += 2
    nedenler.append(f"Haber akışı olumlu (Skor: +{haber_skoru}).")
  elif haber_skoru < 0:
    puan -= 2
    nedenler.append(f"Haber akışı temkinli/olumsuz (Skor: {haber_skoru}).")
  else:
    nedenler.append("Haber akışı dengeli.")

  if puan >= 3:
    karar = "AL"
  elif puan <= -2:
    karar = "SAT"
  else:
    karar = "TUT"

  return (
      karar,
      puan,
      nedenler,
      son_fiyat,
      son_rsi,
      son_sma50,
      son_sma200,
      ideal_alim,
      ideal_satim,
  )


# --- GOOGLE SHEETS ARŞİVİNDEN (STATEFUL) VERİLERİ YÜKLEME FONKSİYONU ---
def arsekten_verileri_yukle():
  varsayilan_kullanicilar = {
      "Devrim": {
          "nakit": 1000000.0,
          "portfoy_hareketleri": [],
          "gunluk_gecmis": [],
          "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date()),
      },
      "Orhan": {
          "nakit": 1000000.0,
          "portfoy_hareketleri": [],
          "gunluk_gecmis": [],
          "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date()),
      },
      "Ali Yiğit": {
          "nakit": 1000000.0,
          "portfoy_hareketleri": [],
          "gunluk_gecmis": [],
          "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date()),
      },
  }
  try:
    response = requests.get(WEBHOOK_URL, timeout=10)
    if response.status_code == 200:
      veri = response.json()
      if isinstance(veri, list) and len(veri) > 0:
        for islem in veri:
          kullanici = islem.get("kullanici", "Devrim")
          if kullanici not in varsayilan_kullanicilar:
            varsayilan_kullanicilar[kullanici] = {
                "nakit": 1000000.0,
                "portfoy_hareketleri": [],
                "gunluk_gecmis": [],
                "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date()),
            }

          tutar_raw = islem.get("toplam_tutar", 0)
          tutar = float(str(tutar_raw).replace(",", ".")) if tutar_raw else 0.0
          
          fiyat_raw = islem.get("fiyat", 0)
          fiyat = float(str(fiyat_raw).replace(",", ".")) if fiyat_raw else 0.0

          lot_raw = islem.get("lot", 0)
          lot = int(float(str(lot_raw).replace(",", "."))) if lot_raw else 0

          islem_turu = islem.get("islem_turu")

          varsayilan_kullanicilar[kullanici]["portfoy_hareketleri"].append({
              "Zaman": islem.get("zaman", ""),
              "Hisse": islem.get("hisse", ""),
              "Tip": islem_turu,
              "Miktar": lot,
              "Fiyat": fiyat,
              "Tutar": tutar,
          })

          if islem_turu == "ALIŞ":
            varsayilan_kullanicilar[kullanici]["nakit"] -= tutar
          elif islem_turu == "SATIŞ":
            varsayilan_kullanicilar[kullanici]["nakit"] += tutar
  except Exception as e:
    print("Veri yükleme hatası:", e)
    pass
  return varsayilan_kullanicilar


# Çoklu Kullanıcı Veritabanı
if "kullanicilar" not in st.session_state:
  st.session_state.kullanicilar = arsekten_verileri_yukle()

# Kenar Çubuğu: Kullanıcı Seçimi / Yönetimi
st.sidebar.header("👤 Yatırımcı Profili")
secilen_kullanici = st.sidebar.selectbox(
    "Aktif Trader Seçin:", list(st.session_state.kullanicilar.keys())
)

with st.sidebar.form("yeni_profil_formu"):
  yeni_kullanici_adi = st.text_input("Veya Yeni Trader Ekle:")
  profil_olustur_btn = st.form_submit_button("Profili Oluştur/Geç")

  if profil_olustur_btn:
    if yeni_kullanici_adi.strip():
      temiz_ad = yeni_kullanici_adi.strip()
      if temiz_ad not in st.session_state.kullanicilar:
        st.session_state.kullanicilar[temiz_ad] = {
            "nakit": 1000000.0,
            "portfoy_hareketleri": [],
            "gunluk_gecmis": [],
            "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date()),
        }
        st.success(f"Hoş geldin {temiz_ad}! 1M TL sermayeniz tanımlandı.")
        st.rerun()
      else:
        st.warning("Bu isimde bir trader zaten var!")

aktif_profil = st.session_state.kullanicilar[secilen_kullanici]

# Günlük Nakit Nemalandırma Kontrolü (%0,12 repo faizi) - Türkiye Saati
bugun_str = str(datetime.datetime.now(TZ_TR).date())
if aktif_profil["son_hesap_tarihi"] != bugun_str:
  faiz_getirisi = aktif_profil["nakit"] * 0.0012
  aktif_profil["nakit"] += faiz_getirisi
  aktif_profil["son_hesap_tarihi"] = bugun_str


tab_tekli, tab_matris, tab_portfoy, tab_liderlik = st.tabs([
    "📊 Tekli Hisse & Derin Analiz",
    "🌐 Tüm Piyasa Sinyal Matrisi (Tarama)",
    f"💼 Sanal Portföy, Radar & Geçmiş ({secilen_kullanici})",
    "🏆 Liderlik & Yatırımcılar Matrisi",
])

with tab_tekli:
  default_index = bist_hisseler.index("THYAO") if "THYAO" in bist_hisseler else 0
  secilen_hisse = st.selectbox(
      "Analiz Etmek İstediğiniz Hisse Senedini Seçin:",
      bist_hisseler,
      index=default_index,
  )

  with st.spinner(f"{secilen_hisse} verileri yükleniyor..."):
    df = veri_cek_ve_hazirla(secilen_hisse)
    haberler, kap_bildirimleri = haberleri_ve_kap_getir(secilen_hisse)

  if df is not None and not df.empty and "Kapanis" in df.columns:
    (
        karar,
        puan,
        nedenler,
        son_fiyat,
        son_rsi,
        son_sma50,
        son_sma200,
        ideal_alim,
        ideal_satim,
    ) = akilli_analiz_hesapla(df, kap_bildirimleri, haberler)

    renk = "🟢" if karar == "AL" else ("🔴" if karar == "SAT" else "🟡")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Son Kapanış Fiyatı", f"{son_fiyat:.2f} TL")
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
    
    # --- YENİ EKLENEN HABERLER VE KAP BİLDİRİMLERİ BÖLÜMÜ ---
    st.markdown("---")
    st.subheader(f"📰 {secilen_hisse} Son Haberler & KAP Bildirimleri")
    col_haber, col_kap = st.columns(2)
    
    with col_haber:
      st.markdown("**Son Haberler**")
      if haberler:
        for h in haberler:
          st.markdown(f"- [{h['baslik']}]({h['link']})")
      else:
        st.info("Yakın zamanda eşleşen haber bulunamadı.")
        
    with col_kap:
      st.markdown("**Son KAP Bildirimleri**")
      if kap_bildirimleri:
        for k in kap_bildirimleri:
          st.markdown(f"- [{k['baslik']}]({k['link']})")
      else:
        st.info("Yakın zamanda eşleşen KAP bildirimi bulunamadı.")
  else:
    st.warning("Bu hisse için yeterli tarihsel veri alınamadı.")

with tab_matris:
  st.subheader("🌐 BİST Genel Tarama ve Sıralı Sinyal Matrisi")
  st.markdown(
      "Sistemdeki tüm hisseler taranır; puanlarına göre en güçlü alım"
      " kağıtlarına **AL 1, AL 2...**, en zayıf satım kağıtlarına **SAT 1,"
      " SAT 2...** derecesi verilir."
  )
  
  tarama_kapsami = st.radio(
      "Tarama Hızı & Kapsamı:",
      ["Sadece Popüler/İlk 50 Hisse (Çok Hızlı ⚡)", "Tüm BİST Hisseleri (Yavaş 🐢)"],
      horizontal=True
  )

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
                return {
                    "Hisse": h_kodu,
                    "Puan": k_puan,
                    "HamKarar": k_karar,
                    "Son Fiyat (TL)": k_fiyat,
                    "RSI": k_rsi,
                    "İdeal Alım": k_alim,
                    "İdeal Satış": k_satim,
                }
        except:
            pass
        return None

    tamamlanan = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        gelecek_islemler = {executor.submit(tekil_tara, h_kodu): h_kodu for h_kodu in hedef_liste}
        for future in concurrent.futures.as_completed(gelecek_islemler):
            sonuc = future.result()
            if sonuc:
                matris_verileri.append(sonuc)
            tamamlanan += 1
            progress_bar.progress(tamamlanan / toplam)

    if matris_verileri:
      df_sonuc = pd.DataFrame(matris_verileri)

      al_grubu = df_sonuc[df_sonuc["HamKarar"] == "AL"].sort_values(by="Puan", ascending=False).reset_index(drop=True)
      sat_grubu = df_sonuc[df_sonuc["HamKarar"] == "SAT"].sort_values(by="Puan", ascending=True).reset_index(drop=True)
      tut_grubu = df_sonuc[df_sonuc["HamKarar"] == "TUT"].sort_values(by="Puan", ascending=False).reset_index(drop=True)

      final_liste = []
      for idx, row in al_grubu.iterrows():
        row["Sinyal Derecesi"] = f"🟢 AL {idx+1}"
        final_liste.append(row)
      for idx, row in sat_grubu.iterrows():
        row["Sinyal Derecesi"] = f"🔴 SAT {idx+1}"
        final_liste.append(row)
      for idx, row in tut_grubu.iterrows():
        row["Sinyal Derecesi"] = f"🟡 TUT"
        final_liste.append(row)

      df_final = pd.DataFrame(final_liste)
      df_final = df_final[["Sinyal Derecesi", "Hisse", "Son Fiyat (TL)", "RSI", "İdeal Alım", "İdeal Satış", "Puan"]]
      
      st.session_state.tarama_sonucu = df_final
      st.success("Tarama ve Dereceli Sıralama Tamamlandı!")
    else:
      st.warning("Tarama sırasında yeterli veri alınamadı.")

  if "tarama_sonucu" in st.session_state:
    df_gosterim = st.session_state.tarama_sonucu
    st.dataframe(
        df_gosterim.style.format({
            "Son Fiyat (TL)": "{:.2f} TL",
            "RSI": "{:.1f}",
            "İdeal Alım": "{:.2f} TL",
            "İdeal Satış": "{:.2f} TL",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # --- HIZLI İŞLEM (AL/SAT) PANELİ ---
    st.markdown("---")
    st.subheader(f"⚡ Hızlı İşlem Paneli ({secilen_kullanici} - Aktif Bakiye: {aktif_profil['nakit']:,.2f} TL)")
    st.markdown("Yukarıdaki matriste gördüğün hisselerden dilediğini seçerek bu ekrandan çıkmadan anında işlem yapabilirsin.")

    with st.form("hizli_islem_formu"):
      col_h1, col_h2, col_h3, col_h4 = st.columns(4)
      with col_h1:
        hizli_hisse = st.selectbox("Hisse Seçin", df_gosterim["Hisse"].tolist())
      with col_h2:
        hizli_tip = st.selectbox("İşlem Tipi", ["ALIŞ", "SATIŞ"])
      with col_h3:
        hizli_lot = st.number_input("Lot Miktarı", min_value=1, value=1000, step=100)
      with col_h4:
        eslesen_satir = df_gosterim[df_gosterim["Hisse"] == hizli_hisse]
        varsayilan_fiyat = float(eslesen_satir["Son Fiyat (TL)"].values[0]) if not eslesen_satir.empty else 10.0
        hizli_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.01, value=varsayilan_fiyat, step=0.05, format="%.2f")

      hizli_onay = st.form_submit_button("🚀 Hızlı Emri Gerçekleştir ve Kaydet")

      if hizli_onay:
        hizli_toplam_tutar = hizli_lot * hizli_fiyat
        zaman_str = datetime.datetime.now(TZ_TR).strftime("%d.%m.%Y %H:%M:%S")

        portfoy_durumu_hizli = {}
        for isl in aktif_profil["portfoy_hareketleri"]:
          hh = isl["Hisse"]
          if hh not in portfoy_durumu_hizli:
            portfoy_durumu_hizli[hh] = 0
          if isl["Tip"] == "ALIŞ":
            portfoy_durumu_hizli[hh] += isl["Miktar"]
          elif isl["Tip"] == "SATIŞ":
            portfoy_durumu_hizli[hh] -= isl["Miktar"]

        if hizli_tip == "ALIŞ":
          if aktif_profil["nakit"] >= hizli_toplam_tutar:
            aktif_profil["nakit"] -= hizli_toplam_tutar
            aktif_profil["portfoy_hareketleri"].append({
                "Zaman": zaman_str, "Hisse": hizli_hisse, "Tip": "ALIŞ",
                "Miktar": hizli_lot, "Fiyat": hizli_fiyat, "Tutar": hizli_toplam_tutar,
            })
            try:
              requests.post(WEBHOOK_URL, json={"zaman": zaman_str, "kullanici": secilen_kullanici, "hisse": hizli_hisse, "islem_turu": "ALIŞ", "lot": hizli_lot, "fiyat": hizli_fiyat, "toplam_tutar": hizli_toplam_tutar}, timeout=5)
            except:
              pass
            st.success(f"✅ {hizli_hisse} için {hizli_lot} lot alış gerçekleştirildi ({secilen_kullanici})!")
            st.rerun()
          else:
            st.error("❌ Yetersiz Nakit Bakiye!")

        elif hizli_tip == "SATIŞ":
          sahip_olunan_lot = portfoy_durumu_hizli.get(hizli_hisse, 0)
          if sahip_olunan_lot >= hizli_lot:
            aktif_profil["nakit"] += hizli_toplam_tutar
            aktif_profil["portfoy_hareketleri"].append({
                "Zaman": zaman_str, "Hisse": hizli_hisse, "Tip": "SATIŞ",
                "Miktar": hizli_lot, "Fiyat": hizli_fiyat, "Tutar": hizli_toplam_tutar,
            })
            try:
              requests.post(WEBHOOK_URL, json={"zaman": zaman_str, "kullanici": secilen_kullanici, "hisse": hizli_hisse, "islem_turu": "SATIŞ", "lot": hizli_lot, "fiyat": hizli_fiyat, "toplam_tutar": hizli_toplam_tutar}, timeout=5)
            except:
              pass
            st.success(f"✅ {hizli_hisse} için {hizli_lot} lot satış gerçekleştirildi ({secilen_kullanici})!")
            st.rerun()
          else:
            st.error(f"❌ Portföyünüzde yeterli {hizli_hisse} yok! (Mevcut: {sahip_olunan_lot} lot)")

with tab_portfoy:
  st.subheader(
      f"💼 Sanal Portföy, Akıllı Radar & Tarihsel Serüven ({secilen_kullanici})"
  )
  st.markdown(
      "Başlangıç sermayeniz **1.000.000 TL**'dir. Nakitleriniz günlük **%0,12"
      " repo faizi** ile nemalanır. Yaptığınız işlemler hem portföyünüze yansır"
      " hem de **Webhook** ile Google E-Tablo arşiviyle senkronize edilir."
  )

  portfoy_durumu = {}
  toplam_varlik_degeri = 0
  hisse_degeri_toplam = 0
  doviz_degeri_toplam = 0
  altin_gumus_degeri_toplam = 0

  for islem in aktif_profil["portfoy_hareketleri"]:
    h = islem["Hisse"]
    tip = islem["Tip"]
    lot = islem["Miktar"]
    fiyat = islem["Fiyat"]

    if h not in portfoy_durumu:
      portfoy_durumu[h] = {"lot": 0, "maliyet_harcama": 0}

    if tip == "ALIŞ":
      portfoy_durumu[h]["lot"] += lot
      portfoy_durumu[h]["maliyet_harcama"] += lot * fiyat
    elif tip == "SATIŞ":
      portfoy_durumu[h]["lot"] -= lot
      if portfoy_durumu[h]["lot"] > 0:
        portfoy_durumu[h]["maliyet_harcama"] -= (
            portfoy_durumu[h]["maliyet_harcama"]
            * (lot / (portfoy_durumu[h]["lot"] + lot))
        )
      else:
        portfoy_durumu[h]["maliyet_harcama"] = 0

  aktif_pozisyonlar = []
  for h, veri in portfoy_durumu.items():
    if veri["lot"] > 0:
      if h in alternatif_varliklar:
        guncel_fiyat = alternatif_fiyat_cek(h)
      else:
        df_p = veri_cek_ve_hazirla(h)
        guncel_fiyat = (
            df_p["Kapanis"].iloc[-1]
            if (df_p is not None and not df_p.empty)
            else (veri["maliyet_harcama"] / veri["lot"])
        )

      piyasa_degeri = veri["lot"] * guncel_fiyat
      maliyet = veri["maliyet_harcama"]
      kar_zarar_tl = piyasa_degeri - maliyet
      kar_zarar_yuzde = (kar_zarar_tl / maliyet * 100) if maliyet > 0 else 0

      toplam_varlik_degeri += piyasa_degeri

      if h in ["USD/TRY", "EUR/TRY", "GBP/TRY"]:
        doviz_degeri_toplam += piyasa_degeri
      elif h in ["Gram Altın (TL)", "Gram Gümüş (TL)"]:
        altin_gumus_degeri_toplam += piyasa_degeri
      else:
        hisse_degeri_toplam += piyasa_degeri

      aktif_pozisyonlar.append({
          "Varlık / Hisse": h,
          "Net Miktar / Lot": veri["lot"],
          "Toplam Maliyet (TL)": maliyet,
          "Güncel Değer (TL)": piyasa_degeri,
          "Kâr / Zarar (TL)": kar_zarar_tl,
          "Kâr / Zarar (%)": kar_zarar_yuzde,
      })

  toplam_toplam = aktif_profil["nakit"] + toplam_varlik_degeri
  toplam_kar_zarar = toplam_toplam - 1000000.0
  toplam_kar_zarar_yuzde = (toplam_kar_zarar / 1000000.0) * 100

  bugun_tarih = str(datetime.datetime.now(TZ_TR).date())
  mevcut_gunluk = aktif_profil["gunluk_gecmis"]
  if not mevcut_gunluk or mevcut_gunluk[-1]["Tarih"] != bugun_tarih:
    mevcut_gunluk.append({
        "Tarih": bugun_tarih,
        "Toplam Varlık": toplam_toplam,
        "Nakit": aktif_profil["nakit"],
        "Hisse": hisse_degeri_toplam,
        "Döviz": doviz_degeri_toplam,
        "Altın & Gümüş": altin_gumus_degeri_toplam,
    })
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
  c4.metric(
      "Toplam Kâr / Zarar",
      f"{toplam_kar_zarar:,.2f} TL",
      f"{toplam_kar_zarar_yuzde:.2f}%",
  )

  st.markdown("---")

  with st.expander(
      "🎯 Anlık Piyasa Radarı: En Güçlü AL Fırsatları & Portföy Risk Alarmları",
      expanded=True,
  ):
    if st.button("📡 Radarı Çalıştır ve Fırsatları Listele"):
      with st.spinner("Piyasa ve portföy taranıyor..."):
        radar_sonuclari = []
        for h_kodu in bist_hisseler[:30]:
          df_r = veri_cek_ve_hazirla(h_kodu)
          if df_r is not None and not df_r.empty and len(df_r) > 30:
            try:
              r_karar, r_puan, _, r_fiyat, r_rsi, _, _, _, _ = (
                  akilli_analiz_hesapla(df_r, [], [])
              )
              radar_sonuclari.append({
                  "Hisse": h_kodu,
                  "Puan": r_puan,
                  "Karar": r_karar,
                  "Fiyat": r_fiyat,
                  "RSI": r_rsi,
              })
            except:
              pass

        if radar_sonuclari:
          df_rad = pd.DataFrame(radar_sonuclari)
          en_iyi_al = (
              df_rad[df_rad["Karar"] == "AL"]
              .sort_values(by="Puan", ascending=False)
              .head(5)
          )

          col_rad1, col_rad2 = st.columns(2)
          with col_rad1:
            st.markdown("### 🟢 En Güçlü AL Fırsatları")
            if not en_iyi_al.empty:
              for idx, row in en_iyi_al.reset_index(drop=True).iterrows():
                st.markdown(
                    f"**{idx+1}. {row['Hisse']}** — Fiyat: {row['Fiyat']:.2f} TL |"
                    f" RSI: {row['RSI']:.1f}"
                )
            else:
              st.info("Güçlü AL sinyali bulunamadı.")

          with col_rad2:
            st.markdown("### 🔴 Riskli / SAT Pozisyonlar")
            aktif_hisseler_listesi = [
                k
                for k, v in portfoy_durumu.items()
                if v["lot"] > 0 and k not in alternatif_varliklar
            ]
            riskli_varliklar = []
            for ah in aktif_hisseler_listesi:
              eslesen = df_rad[df_rad["Hisse"] == ah]
              if not eslesen.empty:
                if eslesen.iloc[0]["Karar"] == "SAT":
                  riskli_varliklar.append(
                      f"⚠️ **{ah}** — SAT sinyali veriyor!"
                  )
            if riskli_varliklar:
              for r in riskli_varliklar:
                st.markdown(r)
            else:
              st.success("Portföyünüzde riskli varlık bulunmuyor.")

  st.markdown("---")

  col_grafik1, col_grafik2 = st.columns(2)
  with col_grafik1:
    st.subheader("📈 Tarihsel Varlık Eğrisi")
    if len(mevcut_gunluk) > 0:
      df_gecmis_varlik = pd.DataFrame(mevcut_gunluk).set_index("Tarih")
      st.line_chart(df_gecmis_varlik[["Toplam Varlık"]])
    else:
      st.info("Veri oluşuyor...")

  with col_grafik2:
    st.subheader("🥧 Varlık Sınıfı Kırılımı (TL)")
    kirilim_df = pd.DataFrame({
        "Varlık Sınıfı": [
            "Nakit / Repo",
            "BİST Hisseler",
            "Döviz",
            "Altın & Gümüş",
        ],
        "Tutar (TL)": [
            aktif_profil["nakit"],
            hisse_degeri_toplam,
            doviz_degeri_toplam,
            altin_gumus_degeri_toplam,
        ],
    }).set_index("Varlık Sınıfı")
    st.bar_chart(kirilim_df)

  st.markdown("---")
  col_islem1, col_islem2 = st.columns(2)

  with col_islem1:
    st.subheader("📝 Emir Girişi (Alış / Satış)")
    secilen_varlik_gecici = st.selectbox(
        "Varlık / Hisse Seçin", tum_islem_varliklari, key="secilen_varlik_input"
    )

    if secilen_varlik_gecici in alternatif_varliklar:
      otomatik_fiyat = alternatif_fiyat_cek(secilen_varlik_gecici)
    else:
      df_gecici = veri_cek_ve_hazirla(secilen_varlik_gecici)
      otomatik_fiyat = (
          float(df_gecici["Kapanis"].iloc[-1])
          if (df_gecici is not None and not df_gecici.empty)
          else 10.0
      )

    with st.form("emir_formu"):
      islem_hisse = secilen_varlik_gecici
      islem_tipi = st.selectbox("İşlem Tipi", ["ALIŞ", "SATIŞ"])
      islem_miktar = st.number_input(
          "Miktar / Lot", min_value=1, value=1000, step=100
      )
      islem_fiyat = st.number_input(
          "Birim Fiyat (TL) [Canlı]",
          min_value=0.01,
          value=float(otomatik_fiyat),
          step=0.05,
          format="%.2f",
      )

      islem_onay = st.form_submit_button("Emri Gerçekleştir ve Tabloya Kaydet")
      if islem_onay:
        toplam_tutar = islem_miktar * islem_fiyat
        zaman_str = datetime.datetime.now(TZ_TR).strftime("%d.%m.%Y %H:%M:%S")

        if islem_tipi == "ALIŞ":
          if aktif_profil["nakit"] >= toplam_tutar:
            aktif_profil["nakit"] -= toplam_tutar
            aktif_profil["portfoy_hareketleri"].append({
                "Zaman": zaman_str,
                "Hisse": islem_hisse,
                "Tip": "ALIŞ",
                "Miktar": islem_miktar,
                "Fiyat": islem_fiyat,
                "Tutar": toplam_tutar,
            })

            try:
              payload = {
                  "zaman": zaman_str,
                  "kullanici": secilen_kullanici,
                  "hisse": islem_hisse,
                  "islem_turu": "ALIŞ",
                  "lot": islem_miktar,
                  "fiyat": islem_fiyat,
                  "toplam_tutar": toplam_tutar,
              }
              requests.post(WEBHOOK_URL, json=payload, timeout=5)
            except:
              pass

            st.success(
                f"✅ {islem_hisse} için {islem_miktar} adet alış"
                f" gerçekleştirildi ({secilen_kullanici}) ve E-Tabloya iletildi!"
            )
            st.rerun()
          else:
            st.error("❌ Yetersiz Nakit Bakiye!")
        elif islem_tipi == "SATIŞ":
          mevcut_lot = portfoy_durumu.get(islem_hisse, {}).get("lot", 0)
          if mevcut_lot >= islem_miktar:
            aktif_profil["nakit"] += toplam_tutar
            aktif_profil["portfoy_hareketleri"].append({
                "Zaman": zaman_str,
                "Hisse": islem_hisse,
                "Tip": "SATIŞ",
                "Miktar": islem_miktar,
                "Fiyat": islem_fiyat,
                "Tutar": toplam_tutar,
            })

            try:
              payload = {
                  "zaman": zaman_str,
                  "kullanici": secilen_kullanici,
                  "hisse": islem_hisse,
                  "islem_turu": "SATIŞ",
                  "lot": islem_miktar,
                  "fiyat": islem_fiyat,
                  "toplam_tutar": toplam_tutar,
              }
              requests.post(WEBHOOK_URL, json=payload, timeout=5)
            except:
              pass

            st.success(
                f"✅ {islem_hisse} için {islem_miktar} adet satış"
                f" gerçekleştirildi ({secilen_kullanici}) ve E-Tabloya iletildi!"
            )
            st.rerun()
          else:
            st.error(
                f"❌ Portföyünüzde yeterli {islem_hisse} yok! (Mevcut:"
                f" {mevcut_lot})"
            )

  with col_islem2:
    st.subheader("📊 Aktif Varlık Dağılımınız")
    if aktif_pozisyonlar:
      df_aktif = pd.DataFrame(aktif_pozisyonlar)
      st.dataframe(
          df_aktif.style.format({
              "Net Miktar / Lot": "{:,}",
              "Toplam Maliyet (TL)": "{:,.2f} TL",
              "Güncel Değer (TL)": "{:,.2f} TL",
              "Kâr / Zarar (TL)": "{:,.2f} TL",
              "Kâr / Zarar (%)": "{:.2f}%",
          }),
          use_container_width=True,
          hide_index=True,
      )
    else:
      st.info("Portföyünüzde şu an aktif varlık yok, nakit durumundasınız.")

  st.markdown("---")
  st.subheader("📜 Geçmiş İşlem Günlüğünüz")
  if aktif_profil["portfoy_hareketleri"]:
    df_gecmis = pd.DataFrame(aktif_profil["portfoy_hareketleri"])
    st.dataframe(
        df_gecmis.style.format({
            "Miktar": "{:,}",
            "Fiyat": "{:.2f} TL",
            "Tutar": "{:,.2f} TL",
        }),
        use_container_width=True,
        hide_index=True,
    )
  else:
    st.write("Henüz işlem geçmişiniz yok.")

  if st.button("🔄 Portföyü Sıfırla (Arşivi Temizle & 1M TL'ye Dön)"):
    st.session_state.kullanicilar = {
        secilen_kullanici: {
            "nakit": 1000000.0,
            "portfoy_hareketleri": [],
            "gunluk_gecmis": [],
            "son_hesap_tarihi": str(datetime.datetime.now(TZ_TR).date()),
        }
    }
    st.rerun()

with tab_liderlik:
  st.subheader("🏆 Yatırımcılar Liderlik & Performans Matrisi")
  st.markdown(
      "Sistemdeki tüm kullanıcıların başlangıç sermayeleri (1.000.000 TL), kalan"
      " repo nakitleri ve canlı varlık değerleri karşılaştırmalı olarak"
      " aşağıda listelenmiştir."
  )

  liderlik_verileri = []
  for kullanici_adi, prof in st.session_state.kullanicilar.items():
    p_durum = {}
    hisse_val = 0
    for isl in prof["portfoy_hareketleri"]:
      h_k = isl["Hisse"]
      t_tip = isl["Tip"]
      m_mik = isl["Miktar"]
      f_fiy = isl["Fiyat"]
      if h_k not in p_durum:
        p_durum[h_k] = {"lot": 0, "maliyet": 0}
      if t_tip == "ALIŞ":
        p_durum[h_k]["lot"] += m_mik
        p_durum[h_k]["maliyet"] += m_mik * f_fiy
      elif t_tip == "SATIŞ":
        p_durum[h_k]["lot"] -= m_mik

    for h_k, v_info in p_durum.items():
      if v_info["lot"] > 0:
        if h_k in alternatif_varliklar:
          g_f = alternatif_fiyat_cek(h_k)
        else:
          df_l = veri_cek_ve_hazirla(h_k)
          g_f = (
              df_l["Kapanis"].iloc[-1]
              if (df_l is not None and not df_l.empty)
              else (v_info["maliyet"] / v_info["lot"])
          )
        hisse_val += v_info["lot"] * g_f

    top_varlik = prof["nakit"] + hisse_val
    k_z_tl = top_varlik - 1000000.0
    k_z_yuzde = (k_z_tl / 1000000.0) * 100

    liderlik_verileri.append({
        "Trader": kullanici_adi,
        "Toplam Varlık (TL)": top_varlik,
        "Kalan Nakit (TL)": prof["nakit"],
        "Varlıklar Değeri (TL)": hisse_val,
        "Net Kâr / Zarar (TL)": k_z_tl,
        "Performans (%)": k_z_yuzde,
    })

  if liderlik_verileri:
    df_lider = pd.DataFrame(liderlik_verileri).sort_values(
        by="Toplam Varlık (TL)", ascending=False
    )
    st.dataframe(
        df_lider.style.format({
            "Toplam Varlık (TL)": "{:,.2f} TL",
            "Kalan Nakit (TL)": "{:,.2f} TL",
            "Varlıklar Değeri (TL)": "{:,.2f} TL",
            "Net Kâr / Zarar (TL)": "{:,.2f} TL",
            "Performans (%)": "{:.2f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )
