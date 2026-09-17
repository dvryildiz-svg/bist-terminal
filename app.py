import json
import tempfile
import os
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- GOOGLE SHEETS BAĞLANTISI (SECRETS KASASI GÜVENLİ) ---
def google_sheets_baglan():
    # Secrets kasasından JSON metnini alıyoruz
    raw_json = st.secrets["GOOGLE_CREDENTIALS_JSON"]
    creds_dict = json.loads(raw_json)
    
    # Python düzeyinde kaçış karakterlerini gerçek alt satırlara dönüştürüyoruz
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Geçici dosya yöntemiyle tüm PEM/Padding hatalarını %100 önlüyoruz
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.json') as f:
        json.dump(creds_dict, f)
        temp_filename = f.name

    try:
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_file(temp_filename, scopes=scopes)
        client = gspread.authorize(creds)
        
        dosya = client.open("BIST_Trader_Arsivi")
        sekme = dosya.worksheet("Portfoy_Arsivi")
        return sekme
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

# --- STREAMLIT ARAYÜZÜ ---
st.title("BIST Trader - Portföy Girişi")

kullanici = st.text_input("Kullanıcı Adı", value="Devrim")
hisse = st.text_input("Varlık / Hisse Sembolü (Örn: GUMUS, THYAO)")
islem_turu = st.selectbox("İşlem Türü", ["ALIŞ", "SATIŞ"])
lot = st.number_input("Lot / Adet", min_value=0.0, format="%.2f")
fiyat = st.number_input("İşlem Fiyatı", min_value=0.0, format="%.2f")

# Kaydet Butonu
if st.button("İşlemi Kaydet"):
    if hisse and lot > 0 and fiyat > 0:
        try:
            sekme = google_sheets_baglan()
            
            zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            toplam_tutar = lot * fiyat
            
            yeni_islem = [zaman, kullanici, hisse.upper(), islem_turu, lot, fiyat, toplam_tutar]
            sekme.append_row(yeni_islem)
            
            st.success(f"Başarılı! {hisse} işlemi Portfoy_Arsivi sekmesine kaydedildi.")
            
        except Exception as e:
            st.error(f"Hata Detayı: {type(e).__name__} - {str(e)}")
    else:
        st.warning("Lütfen hisse sembolü, lot ve fiyat bilgilerini eksiksiz girin.")
