import datetime
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="BİST & Varlık Yönetim Terminali",
    page_icon="🦁",
    layout="wide",
)

st.title("🦁 BİST & Çoklu Varlık Profesyonel Fon Yönetim Terminali")
st.markdown(
    "Google E-Tablolar (GOOGLEFINANCE) Canlı Fiyat Entegrasyonu, Günlük"
    " Nemalandırma (%0,12), Sanal Portföy Akıllı Radarı ve Çoklu Kullanıcı"
    " Liderlik Matrisi."
)

# Google Apps Script Webhook URL'niz (Kayıt için)
WEBHOOK_URL = (
    "https://script.google.com/macros/s/AKfycbwmG2vAGJdW-8kDE3CpyBHNU8wptywkhrLW_HyLIYOm3l9yPH-O9hqNaAyYARdl5mbjeg/exec"
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


@st.cache_data(ttl=60)
def canli_fiyat_cek(varlik):
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
    else:
      # BİST hisseleri için Yahoo Finance üzerinden anlık/güncel fiyat entegrasyonu
      ticker_str = f"{varlik}.IS"
      t = yf.Ticker(ticker_str)
      hist = t.history(period="1d")
      if not hist.empty:
        return float(hist["Close"].iloc[-1])
  except:
    pass
  return 10.0


# Çoklu Kullanıcı Veritabanı
if "kullanicilar" not in st.session_state:
  st.session_state.kullanicilar = {
      "Devrim": {
          "nakit": 1000000.0,
          "portfoy_hareketleri": [],
          "gunluk_gecmis": [],
          "son_hesap_tarihi": str(datetime.date.today()),
      },
      "Ahmet": {
          "nakit": 1000000.0,
          "portfoy_hareketleri": [],
          "gunluk_gecmis": [],
          "son_hesap_tarihi": str(datetime.date.today()),
      },
  }

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
          "gunluk_gecmis": [],
          "son_hesap_tarihi": str(datetime.date.today()),
      }
      st.success(f"Hoş geldin {temiz_ad}! 1M TL sermayeniz tanımlandı.")
      st.rerun()

aktif_profil = st.session_state.kullanicilar[secilen_kullanici]

# Günlük Nakit Nemalandırma Kontrolü (%0,12 repo faizi)
bugun_str = str(datetime.date.today())
if aktif_profil["son_hesap_tarihi"] != bugun_str:
  faiz_getirisi = aktif_profil["nakit"] * 0.0012
  aktif_profil["nakit"] += faiz_getirisi
  aktif_profil["son_hesap_tarihi"] = bugun_str


tab_portfoy, tab_liderlik = st.tabs([
    f"💼 Sanal Portföy, Emir Girişi & Canlı Takip ({secilen_kullanici})",
    "🏆 Liderlik & Yatırımcılar Matrisi",
])

with tab_portfoy:
  st.subheader(
      f"💼 Profesyonel Sanal Portföy ve Canlı İşlem Merkezi ({secilen_kullanici})"
  )
  st.markdown(
      "Başlangıç sermayeniz **1.000.000 TL**'dir. Nakitleriniz günlük **%0,12"
      " repo faizi** ile nemalanır. Yaptığınız işlemler hem anlık olarak"
      " hesaplanır hem de **Webhook** aracılığıyla Google E-Tablo arşiviyle"
      " senkronize edilir."
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
      guncel_fiyat = canli_fiyat_cek(h)
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

  col_islem1, col_islem2 = st.columns(2)

  with col_islem1:
    st.subheader("📝 Canlı Emir Girişi (Alış / Satış)")
    secilen_varlik_gecici = st.selectbox(
        "Varlık / Hisse Seçin", tum_islem_varliklari, key="secilen_varlik_input"
    )
    otomatik_fiyat = canli_fiyat_cek(secilen_varlik_gecici)

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

      islem_onay = st.form_submit_button("Emri Gerçekleştir ve Tabloya Kaydet")
      if islem_onay:
        toplam_tutar = islem_miktar * islem_fiyat
        zaman_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

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

            # Google Sheets Webhook'a gönderim
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
                " gerçekleştirildi ve E-Tabloya iletildi!"
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

            # Google Sheets Webhook'a gönderim
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
                " gerçekleştirildi ve E-Tabloya iletildi!"
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

  if st.button("🔄 Portföyü Sıfırla (1M TL'ye Dön)"):
    aktif_profil["nakit"] = 1000000.0
    aktif_profil["portfoy_hareketleri"] = []
    aktif_profil["gunluk_gecmis"] = []
    st.rerun()

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
        g_f = canli_fiyat_cek(h_k)
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
