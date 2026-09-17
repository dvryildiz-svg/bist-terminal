import base64
import json
import tempfile
import os
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- KESİN ÇÖZÜM: GÜVENLİ BASE64 ÇÖZÜCÜ MOTOR ---
def google_sheets_baglan():
    b64_encoded_key = st.secrets["b64_key"]
    
    # Base64 baytlarını çözüyoruz ve utf-8 decode ederken hatalı baytları atlayarak güvenli hale getiriyoruz
    json_bytes = base64.b64decode(b64_encoded_key)
    json_str = json_bytes.decode('utf-8', errors='ignore')
    creds_dict = json.loads(json_str)

    # Geçici dosyaya yazarak gspread / google-auth kütüphanesine sunuyoruz
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
