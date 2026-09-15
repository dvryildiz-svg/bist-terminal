import datetime
from feedparser import parse
from isyatirimhisse import fetch_stock_data
import pandas as streamlit_pandas
import streamlit as st

st.set_page_config(
    page_title="BİST Akıllı Karar Destek & KAP Terminali",
    page_icon="📈",
    layout="wide",
)

st.title("📈 BİST Akıllı Karar Destek ve Simülasyon Terminali")
st.markdown(
    "Teknik indikatörler, haber duygu analizi ve gerekçelendirilmiş AL/SAT/TUT"
    " sinyalleri."
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


def akilli_analiz_uret(df, haberler, kap_bildirimleri):
   nedenler = []
  puan = 0

  # Teknik Analiz Değerlendirmesi
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

  if son_rsi < 35:
    puan += 2
    nedenler.append(
        f"RSI aşırı satım bölgesinde ({son_rsi:.1f}), toparlanma potansiyeli"
        " yüksek."
    )
  elif son_rsi > 65:
    puan -= 2
    nedenler.append(
        f"RSI aşırı alım bölgesinde ({son_rsi:.1f}), kar satışı riski var."
    )
  else:
    nedenler.append(f"RSI nötr seviyede ({son_rsi:.1f}).")

  if son_fiyat > son_sma50:
    puan += 1
    nedenler.append("Fiyat 50 günlük hareketli ortalamanın üzerinde (Kısa pozitif trend).")
  else:
    puan -= 1
    nedenler.append("Fiyat 50 günlük hareketli ortalamanın altında (Kısa zayıf seyir).")

  if son_fiyat > son_sma200:
    puan += 2
    nedenler.append("Fiyat 200 günlük ana trend çizgisinin üzerinde (Uzun vade güçlü).")
  else:
    puan -= 2
    nedenler.append("Fiyat 200 günlük ana trend çizgisinin altında (Uzun vade baskı altında).")

  # Haber ve KAP Duygu Analizi
  olumlu_kelimeler = [
      "sözleşme",
      "ihale",
      "kar",
      "rekor",
      "artış",
      "onay",
      "başarı",
      "yatırım",
      "büyüme",
      "güçlü",
  ]
  olumsuz_kelimeler = [
      "zarar",
      "ceza",
      "soruşturma",
      "dava",
      "borç",
      "kriz",
      "düşüş",
      "kayıp",
      "şüpheli",
  ]

  haber_skoru = 0
  taranan_metinler = [k["baslik"].lower() for k in kap_bildirimleri] + [
      h["baslik"].lower() for h in haberler
  ]

  for metin in taranan_metinler:
    for kelime in olumlu_kelimeler:
      if kelime in metin:
        haber_skoru += 1
    for kelime in olumsuz_kelimeler:
      if kelime in metin:
        haber_skoru -= 1

  if haber_skoru > 0:
    puan += 2
    nedenler.append(
        f"Son KAP bildirimleri ve haber akışında olumlu ton hakim (Skor:"
        f" +{haber_skoru})."
    )
  elif haber_skoru < 0:
    puan -= 2
    nedenler.append(
        f"Haber akışında ve bildirimlerde temkinli/olumsuz başlıklar var (Skor:"
        f" {haber_skoru})."
    )
  else:
    nedenler.append("Haber akışında nötr ve dengeli bir akış gözleniyor.")

  # Karar Belirleme
  if puan >= 3:
    karar = "AL"
    renk = "🟢"
  elif puan <= -2:
    karar = "SAT"
    renk = "🔴"
  else:
    karar = "TUT (NÖTR)"
    renk = "🟡"

  return karar, renk, nedenler, son_fiyat, son_rsi, son_sma50, son_sma200


with st.spinner(f"{secilen_hisse} verileri, haberler ve akıllı analiz işleniyor..."):
  df = veri_cek_ve_hazirla(secilen_hisse)
  haberler, kap_bildirimleri = haberleri_ve_kap_getir(secilen_hisse)

if df is not None and not df.empty and "Kapanis" in df.columns:
  karar, renk, nedenler, son_fiyat, son_rsi, son_sma50, son_sma200 = (
      akilli_analiz_uret(df, haberler, kap_bildirimleri)
  )

  # Üst Özet Metrikleri
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Son Fiyat", f"{son_fiyat:.2f} TL")
  col2.metric("RSI (14)", f"{son_rsi:.2f}")
  col3.metric("SMA 50", f"{son_sma50:.2f} TL")
  col4.metric("SMA 200", f"{son_sma200:.2f} TL")

  # Akıllı Karar Paneli
  st.markdown("---")
  st.subheader(f"🧠 Akıllı Karar Önerisi: {renk} **{karar}**")
  with st.expander(
      "🔍 Bu Kararın Gerekçeleri (Teknik + Haber Duygu Analizi)", expanded=True
  ):
    for neden in nedenler:
      st.markdown(f"- {neden}")
  st.markdown("---")

  st.subheader(f"{secilen_hisse} Fiyat Grafiği")
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
