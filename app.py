import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="BIST Trader Terminal", layout="wide")

st.title("BIST Trader - Portföy ve Analiz Terminali")

# Google Apps Script Webhook URL'niz
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwmG2vAGJdW-8kDE3CpyBHNU8wptywkhrLW_HyLIYOm3l9yPH-O9hqNaAyYARdl5mbjeg/exec"

# Sekmeler oluşturuyoruz
tab1, tab2 = st.tabs(["📊 İşlem Girişi & Özet", "📈 Portföy Analizi & Grafikler"])

with tab1:
    st.subheader("Yeni İşlem Kaydı")
    
    col1, col2 = st.columns(2)
    with col1:
        kullanici = st.text_input("Kullanıcı Adı", value="Devrim")
        hisse = st.text_input("Varlık / Hisse Sembolü (Örn: GUMUS, THYAO)")
        islem_turu = st.selectbox("İşlem Türü", ["ALIŞ", "SATIŞ"])
        
    with col2:
        lot = st.number_input("Lot / Adet", min_value=0.0, format="%.2f", value=1.0)
        fiyat = st.number_input("İşlem Fiyatı", min_value=0.0, format="%.2f", value=100.0)

    if st.button("İşlemi Kaydet"):
        if hisse and lot > 0 and fiyat > 0:
            try:
                zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                toplam_tutar = lot * fiyat
                
                payload = {
                    "zaman": zaman,
                    "kullanici": kullanici,
                    "hisse": hisse.upper(),
                    "islem_turu": islem_turu,
                    "lot": lot,
                    "fiyat": fiyat,
                    "toplam_tutar": toplam_tutar
                }
                
                response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                result = response.json()
                
                if result.get("status") == "success":
                    st.success(f"Başarılı! {hisse.upper()} işlemi arşive kaydedildi.")
                else:
                    st.error(f"Kayıt Hatası: {result.get('message', 'Bilinmeyen hata')}")
                    
            except Exception as e:
                st.error(f"Bağlantı Hatası: {type(e).__name__} - {str(e)}")
        else:
            st.warning("Lütfen tüm alanları eksiksiz doldurun.")

with tab2:
    st.subheader("Portföy Dağılımı ve Analizler")
    st.info("Bu alanda portföyündeki varlıkların ağırlıkları, kâr/zarar durumları ve performans grafikleri yer alacak.")
    
    # Örnek Analiz Alanı (Google Sheets'ten veri okuma entegrasyonu için altyapı)
    # İlerleyen adımlarda buraya doğrudan varlık özet tablolarını ve Streamlit grafiklerini (st.line_chart / st.bar_chart) ekleyebiliriz.
    st.markdown("---")
    st.write("🚀 **Piyasa Takip Modülü ve Detaylı Grafik Ekranları** aktif hale getirilmeye hazır.")
