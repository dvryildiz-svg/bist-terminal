import datetime
from feedparser import parse
from isyatirimhisse import fetch_stock_data
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="BİST & Varlık Yönetim Terminali",
    page_icon="🦅",
    layout="wide",
)

st.title("🦅 BİST & Çoklu Varlık Profesyonel Fon Yönetim Terminali")
st.markdown(
    "Sıralı Sinyaller (AL1, SAT1...), Canlı Döviz/Altın/Gümüş Fiyatları, Günlük"
    " Nemalandırma (%0,12) ve Çoklu Kullanıcı Liderlik Matrisi."
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

alternatif_varliklar = [
    "USD/TRY",
    "EUR/TRY",
    "GBP/TRY",
    "Gram Altın (TL)",
    "Gram Gümüş (TL)",
]
tum_islem_varliklari = sorted(bist_hisseler) + alternatif_varliklar

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


# Çoklu Kullanıcı Veritabanı (Session State Ana Havuzu)
if "kullanicilar" not in st.session_state:
  st.session_state.kullanicilar = {
      "Devrim": {
          "nakit": 1000000.0,
          "portfoy_hareketleri": [],
          "son_hesap_tarihi": str(datetime.date.today()),
      },
      "Ahmet": {
          "nakit": 1000000.0,
          "portfoy_hareketleri": [],
          "son_hesap_tarihi": str(datetime.date.today()),
      },
  }

# Kenar Çubuğu: Kullanıcı Seçimi / Yönetimi
st.sidebar.header("👤 Yatırımcı Profili")
secilen_kullanici = st.sidebar.selectbox(
    "Aktif Trader Seçin:", list(st.session_state.kullanicilar.keys())
)

yeni_kullanici_adi = st.sidebar.text_input("Veya Yeni Trader Ekle:")
if st.sidebar.button("Profili Oluştur/Geç"):
  if yeni_kullanici_adi.strip():
    temiz_ad = yeni_kullanici_adi.strip()
    if temiz_ad not in st.session_state.kullanicilar:
      st.session_state.kullanicilar[temiz_ad] = {
          "nakit": 1000000.0,
          "portfoy_hareketleri": [],
          "son_hesap_tarihi": str(datetime.date.today()),
      }
      st.success(f"Hoş geldin {temiz_ad}! 1M TL sermayeniz tanımlandı.")
      st.rerun()

aktif_profil = st.session_state.kullanicilar[secilen_kullanici]

# Günlük Nakit Nemalandırma Kontrolü (%0,12 günlük repo faizi)
bugun_str = str(datetime.date.today())
if aktif_profil["son_hesap_tarihi"] != bugun_str:
  faiz_getirisi = aktif_profil["nakit"] * 0.0012
  aktif_profil["nakit"] += faiz_getirisi
  aktif_profil["son_hesap_tarihi"] = bugun_str


tab_tekli, tab_matris, tab_portfoy, tab_liderlik = st.tabs([
    "📊 Tekli Hisse & Derin Analiz",
    "🌐 Tüm Piyasa Sinyal Matrisi (Tarama)",
    f"💼 Sanal Portföy ({secilen_kullanici})",
    "🏆 Liderlik & Yatırımcılar Matrisi",
])

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
  else:
    st.warning("Veri alınamadı.")

with tab_matris:
  st.subheader("🌐 BİST Genel Tarama ve Sıralı Sinyal Matrisi")
  st.markdown(
      "Sistemdeki tüm hisseler taranır; puanlarına göre en güçlü alım"
      " kağıtlarına **AL 1, AL 2...**, en zayıf satım kağıtlarına **SAT 1,"
      " SAT 2...** derecesi verilir."
  )

  if st.button("🚀 Tüm Piyasayı Tara ve Sıralı Matrisi Oluştur"):
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
              k_puan,
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
              "Puan": k_puan,
              "HamKarar": k_karar,
              "Son Fiyat (TL)": k_fiyat,
              "RSI": k_rsi,
              "İdeal Alım": k_alim,
              "İdeal Satış": k_satim,
          })
        except:
          pass
      progress_bar.progress((i + 1) / toplam)

    if matris_verileri:
      df_sonuc = pd.DataFrame(matris_verileri)

      al_grubu = (
          df_sonuc[df_sonuc["HamKarar"] == "AL"]
          .sort_values(by="Puan", ascending=False)
          .reset_index(drop=True)
      )
      sat_grubu = (
          df_sonuc[df_sonuc["HamKarar"] == "SAT"]
          .sort_values(by="Puan", ascending=True)
          .reset_index(drop=True)
      )
      tut_grubu = (
          df_sonuc[df_sonuc["HamKarar"] == "TUT"]
          .sort_values(by="Puan", ascending=False)
          .reset_index(drop=True)
      )

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
      df_final = df_final[[
          "Sinyal Derecesi",
          "Hisse",
          "Son Fiyat (TL)",
          "RSI",
          "İdeal Alım",
          "İdeal Satış",
          "Puan",
      ]]

      st.success("Tarama ve Dereceli Sıralama Tamamlandı!")
      st.dataframe(
          df_final.style.format({
              "Son Fiyat (TL)": "{:.2f} TL",
              "RSI": "{:.1f}",
              "İdeal Alım": "{:.2f} TL",
              "İdeal Satış": "{:.2f} TL",
          }),
          use_container_width=True,
          hide_index=True,
      )
    else:
      st.warning("Tarama sırasında yeterli veri alınamadı.")

with tab_portfoy:
  st.subheader(
      f"💼 Sanal Portföy & Çoklu Varlık Terminali ({secilen_kullanici})"
  )
  st.markdown(
      "Başlangıç sermayeniz **1.000.000 TL**'dir. Boşta kalan nakitleriniz"
      " günlük **%0,12 repo faizi** ile nemalanır. BİST hisseleri, Döviz (USD,"
      " EUR, GBP) ve Kıymetli Madenler (Altın, Gümüş) alıp satabilirsiniz."
  )

  portfoy_durumu = {}
  toplam_varlik_degeri = 0

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

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Toplam Varlık", f"{toplam_toplam:,.2f} TL")
  c2.metric("Nakit Bakiye (Nemalanan)", f"{aktif_profil['nakit']:,.2f} TL")
  c3.metric("Varlıkların Piyasa Değeri", f"{toplam_varlik_degeri:,.2f} TL")
  c4.metric(
      "Toplam Kâr / Zarar",
      f"{toplam_kar_zarar:,.2f} TL",
      f"{toplam_kar_zarar_yuzde:.2f}%",
  )

  st.markdown("---")
  col_islem1, col_islem2 = st.columns(2)

  with col_islem1:
    st.subheader("📝 Emir Girişi (Alış / Satış)")

    # Seçilen varlığın anlık fiyatını önden çekelim ki varsayılan olarak yazabilelim
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
          "Birim Fiyat (TL)",
          min_value=0.01,
          value=float(otomatik_fiyat),
          step=0.05,
          format="%.2f",
      )

      islem_onay = st.form_submit_button("Emri Gerçekleştir")
      if islem_onay:
        toplam_tutar = islem_miktar * islem_fiyat
        if islem_tipi == "ALIŞ":
          if aktif_profil["nakit"] >= toplam_tutar:
            aktif_profil["nakit"] -= toplam_tutar
            aktif_profil["portfoy_hareketleri"].append({
                "Zaman": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Hisse": islem_hisse,
                "Tip": "ALIŞ",
                "Miktar": islem_miktar,
                "Fiyat": islem_fiyat,
                "Tutar": toplam_tutar,
            })
            st.success(
                f"✅ {islem_hisse} için {islem_miktar} adet alış"
                " gerçekleştirildi!"
            )
            st.rerun()
          else:
            st.error("❌ Yetersiz Nakit Bakiye!")
        elif islem_tipi == "SATIŞ":
          mevcut_lot = portfoy_durumu.get(islem_hisse, {}).get("lot", 0)
          if mevcut_lot >= islem_miktar:
            aktif_profil["nakit"] += toplam_tutar
            aktif_profil["portfoy_hareketleri"].append({
                "Zaman": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Hisse": islem_hisse,
                "Tip": "SATIŞ",
                "Miktar": islem_miktar,
                "Fiyat": islem_fiyat,
                "Tutar": toplam_tutar,
            })
            st.success(
                f"✅ {islem_hisse} için {islem_miktar} adet satış"
                " gerçekleştirildi!"
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
    if st.button("🔄 Portföyü Sıfırla (1M TL'ye Dön)"):
      aktif_profil["nakit"] = 1000000.0
      aktif_profil["portfoy_hareketleri"] = []
      st.rerun()
  else:
    st.write("Henüz işlem geçmişiniz yok.")

with tab_liderlik:
  st.subheader("🏆 Yatırımcılar Liderlik & Performans Matrisi")
  st.markdown(
      "Sistemdeki tüm kullanıcıların portföy değerleri, nakitleri ve toplam"
      " kâr/zarar durumları karşılaştırmalı olarak aşağıda listelenmiştir."
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
        "Nakit (TL)": prof["nakit"],
        "Varlıklar (TL)": hisse_val,
        "Kâr / Zarar (TL)": k_z_tl,
        "Performans (%)": k_z_yuzde,
    })

  if liderlik_verileri:
    df_lider = pd.DataFrame(liderlik_verileri).sort_values(
        by="Toplam Varlık (TL)", ascending=False
    )
    st.dataframe(
        df_lider.style.format({
            "Toplam Varlık (TL)": "{:,.2f} TL",
            "Nakit (TL)": "{:,.2f} TL",
            "Varlıklar (TL)": "{:,.2f} TL",
            "Kâr / Zarar (TL)": "{:,.2f} TL",
            "Performans (%)": "{:.2f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )
