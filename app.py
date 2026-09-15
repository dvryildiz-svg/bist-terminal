import datetime
from feedparser import parse
from isyatirimhisse import fetch_stock_data
import pandas as streamlit_pandas
import streamlit as st

st.set_page_config(
    page_title="BİST Profesyonel Karar Destek & KAP Terminali",
    page_icon="📈",
    layout="wide",
)

st.title("📈 BİST Profesyonel Simülasyon ve Karar Destek Terminali")
st.markdown(
    "İş Yatırım anlık verileri, teknik indikatörler, canlı piyasa haberleri ve"
    " KAP bildirimleri."
)

bist_hisseler = sorted([
    "AEFES",
    "AGHOL",
    "AHGAZ",
    "AKBNK",
    "AKCNS",
    "AKFGY",
    "AKSA",
    "AKSEN",
    "ALARK",
    "ALBRK",
    "ALFAS",
    "ARCLK",
    "ASELS",
    "ASTOR",
    "BERA",
    "BIENY",
    "BIMAS",
    "BOBET",
    "BRSAN",
    "BRYAT",
    "BUCIM",
    "CCOLA",
    "CIMSA",
    "CWENE",
    "DOAS",
    "DOHOL",
    "ECZYT",
    "EGEEN",
    "EKGYO",
    "ENERY",
    "ENKAI",
    "EREGL",
    "EUPWR",
    "FROTO",
    "GARAN",
    "GESAN",
    "GLYHO",
    "GUBRF",
    "HEKTS",
    "ISCTR",
    "KCHOL",
    "KONTR",
    "KOZAA",
    "KOZAL",
    "KRDMD",
    "ODAS",
    "PETKM",
    "PGSUS",
    "SAHOL",
    "SASA",
    "SISE",
    "TAVHL",
    "THYAO",
    "TOASO",
    "TUPRS",
    "YKBNK",
])

default_index = bist_hisseler.index("SASA") if "SASA" in bist_hisseler else 0
secilen_hisse = st.selectbox(
    "Analiz Etmek İstediğiniz Hisse Senedini Seçin:",
    bist_hisseler,
    index=default_index,
)

bitis_tarihi = datetime.datetime.now().strftime("%d-%m-%Y")
baslangic_tarihi = (
    datetime.datetime.now() - datetime.timedelta(days=365)
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
        df["Tarih"] = streamlit_pandas.to_datetime(
            df[tarih_kolonu], format="%d-%m-%Y", errors="coerce"
        )
        df = df.dropna(subset=["Tarih"]).sort_values("Tarih")
        df["Kapanis"] = streamlit_pandas.to_numeric(
            df[kapanis_kolonu], errors="coerce"
        )
        return df
  except Exception as e:
    st.error(f"Veri çekilirken hata oluştu: {e}")
  return None


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


with st.spinner(f"{secilen_hisse} verileri ve resmi bildirimler yükleniyor..."):
  df = veri_cek_ve_hazirla(secilen_hisse)
  haberler, kap_bildirimleri = haberleri_ve_kap_getir(secilen_hisse)

if df is not None and not df.empty and "Kapanis" in df.columns:
  delta = df["Kapanis"].diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
  rs = gain / loss
  df["RSI"] = 100 - (100 / (1 + rs))

  df["SMA50"] = df["Kapanis"].rolling(window=50).mean()
  df["SMA200"] = df["Kapanis"].rolling(window=200).mean()

  son_fiyat = df["Kapanis"].iloc[-1]
  son_rsi = df["RSI"].iloc[-1]
  son_sma50 = df["SMA50"].iloc[-1]
  son_sma200 = df["SMA200"].iloc[-1]

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Son Fiyat", f"{son_fiyat:.2f} TL")
  col2.metric("RSI (14)", f"{son_rsi:.2f}")
  col3.metric("SMA 50", f"{son_sma50:.2f} TL")
  col4.metric("SMA 200", f"{son_sma200:.2f} TL")

  st.subheader(f"{secilen_hisse} Fiyat ve Hareketli Ortalamalar")
  st.line_chart(df.set_index("Tarih")[["Kapanis", "SMA50", "SMA200"]])

  tab_kap, tab_haber = st.tabs(
      ["📢 Resmi KAP Bildirimleri", "📰 Piyasa & Basın Haberleri"]
  )
  with tab_kap:
    if kap_bildirimleri:
      for k in kap_bildirimleri:
        st.markdown(f"- **[{k['zaman']}]** [{k['baslik']}]({k['link']})")
    else:
      st.info("Bu hisse için resmi bildirim bulunamadı.")
  with tab_haber:
    if haberler:
      for h in haberler:
        st.markdown(f"- **[{h['zaman']}]** [{h['baslik']}]({h['link']})")
    else:
      st.info("Basın akışı bulunamadı.")
else:
  st.warning("Veri işlenemedi veya sütun yapısı uyumsuz.")
