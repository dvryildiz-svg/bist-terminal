import datetime
from feedparser import parse
from isyatirimhisse import fetch_stock_data
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="BİST Akıllı Karar Destek & Sinyal Matrisi",
    page_icon="📈",
    layout="wide",
)

st.title("📈 BİST Profesyonel Karar Destek ve Sinyal Matrisi")
st.markdown(
    "Teklifler, teknik indikatörler, haber duygu analizi ve tüm piyasa tarama"
    " modülü."
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
        df["Tarih"] = pd.to_datetime(
            df[tarih_kolonu], format="%d-%m-%Y", errors="coerce"
        )
        df = df.dropna(subset=["Tarih"]).sort_values("Tarih")
        df["Kapanis"] = pd.to_numeric(df[kapanis_kolonu], errors="coerce")
        return df
  except:
    pass
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

  # İdeal Alım ve Satım Seviyeleri
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
    renk = "🟢"
  elif puan <= -2:
    karar = "SAT"
    renk = "🔴"
  else:
    karar = "TUT (NÖTR)"
    renk = "🟡"

  return (
      karar,
      renk,
      nedenler,
      son_fiyat,
      son_rsi,
      son_sma50,
      son_sma200,
      ideal_alim,
      ideal_satim,
  )


tab_tekli, tab_matris = st.tabs(
    ["📊 Tekli Hisse & Derin Analiz", "🌐 Tüm Piyasa Sinyal Matrisi (Tarama)"]
)

with tab_tekli:
  default_index = bist_hisseler.index("SASA") if "SASA" in bist_hisseler else 0
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
        renk,
        nedenler,
        son_fiyat,
        son_rsi,
        son_sma50,
        son_sma200,
        ideal_alim,
        ideal_satim,
    ) = akilli_analiz_hesapla(df, kap_bildirimleri, haberler)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Son Fiyat", f"{son_fiyat:.2f} TL")
    col2.metric("RSI (14)", f"{son_rsi:.1f}")
    col3.metric("İdeal Alım (Destek)", f"{ideal_alim:.2f} TL")
    col4.metric("İdeal Satış (Direnç)", f"{ideal_satim:.2f} TL")

    st.markdown("---")
    st.subheader(f"🧠 Akıllı Karar Önerisi: {renk} **{karar}**")
    with st.expander(
        "🔍 Gerekçeler ve Detaylı Analiz", expanded=True
    ):
      for n in nedenler:
        st.markdown(f"- {n}")
    st.markdown("---")

    st.subheader(f"{secilen_hisse} Fiyat Grafiği")
    st.line_chart(df.set_index("Tarih")[["Kapanis", "SMA50", "SMA200"]])

    t_kap, t_hab = st.tabs(
        ["📢 Resmi KAP Bildirimleri", "📰 Piyasa & Basın Haberleri"]
    )
    with t_kap:
      for k in kap_bildirimleri:
        st.markdown(f"- **[{k['zaman']}]** [{k['baslik']}]({k['link']})")
    with t_hab:
      for h in haberler:
        st.markdown(f"- **[{h['zaman']}]** [{h['baslik']}]({h['link']})")
  else:
    st.warning("Veri alınamadı.")

with tab_matris:
  st.subheader("🌐 BİST Genel Tarama ve Fırsat Matrisi")
  st.markdown(
      "Sistemdeki tüm hisseler taranarak anlık sinyaller ve ideal seviyeler"
      " hesaplanıyor."
  )

  if st.button("🚀 Tüm Piyasayı Tara ve Matrisi Oluştur"):
    matris_verileri = []
    progress_bar = st.progress(0)
    toplam = len(bist_hisseler)

    for i, h_kodu in enumerate(bist_hisseler):
      df_m = veri_cek_ve_hazirla(h_kodu)
      _, kap_m = haberleri_ve_kap_getir(h_kodu)
      if df_m is not None and not df_m.empty and len(df_m) > 30:
        try:
          (
              k_karar,
              k_renk,
              _,
              k_fiyat,
              k_rsi,
              _,
              _,
              k_alim,
              k_satim,
          ) = akilli_analiz_hesapla(df_m, kap_m, [])
          matris_verileri.append({
              "Hisse": h_kodu,
              "Son Fiyat (TL)": f"{k_fiyat:.2f}",
              "RSI": f"{k_rsi:.1f}",
              "Sinyal": f"{k_renk} {k_karar}",
              "İdeal Alım": f"{k_alim:.2f} TL",
              "İdeal Satış": f"{k_satim:.2f} TL",
          })
        except:
          pass
      progress_bar.progress((i + 1) / toplam)

    if matris_verileri:
      df_sonuc = pd.DataFrame(matris_verileri)
      st.success("Tarama tamamlandı!")
      st.dataframe(df_sonuc, use_container_width=True)
    else:
      st.warning("Tarama sırasında yeterli veri alınamadı.")
