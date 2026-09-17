import streamlit as st
import requests
import json
from datetime import datetime

# --- STREAMLIT ARAYÜZÜ ---
st.title("BIST Trader - Portföy Girişi")

kullanici = st.text_input("Kullanıcı Adı", value="Devrim")
hisse = st.text_input("Varlık / Hisse Sembolü (Örn: GUMUS, THYAO)")
islem_turu = st.selectbox("İşlem Türü", ["ALIŞ", "SATIŞ"])
lot = st.number_input("Lot / Adet", min_value=0.0, format="%.2f")
fiyat = st.number_input("İşlem Fiyatı", min_value=0.0, format="%.2f")

# Google Apps Script Webhook URL'niz
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwmG2vAGJdW-8kDE3CpyBHNU8wptywkhrLW_HyLIYOm3l9yPH-O9hqNaAyYARdl5mbjeg/exec"

# Kaydet Butonu
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
            
            # Google Sheets'e HTTP POST isteği gönderiyoruz
            response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            result = response.json()
            
            if result.get("status") == "success":
                st.success(f"Başarılı! {hisse} işlemi Portfoy_Arsivi sekmesine kaydedildi.")
            else:
                st.error(f"Google Sheets Hatası: {result.get('message', 'Bilinmeyen hata')}")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {type(e).__name__} - {str(e)}")
    else:
        st.warning("Lütfen hisse sembolü, lot ve fiyat bilgilerini eksiksiz girin.")
