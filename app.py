import base64
import json
import tempfile
import os
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- ALTERNATİF VE KESİN ÇÖZÜM MOTORU ---
def google_sheets_baglan():
    raw_pk = st.secrets["raw_private_key"]
    
    # Python'un bayt kodlayıcısı ile tüm bozuk satır sonlarını ve kaçışları temizliyoruz
    # Bu yöntem cryptography kütüphanesinin PEM okuyucusundaki "Invalid symbol 61" hatasını tamamen bypass eder.
    cleaned_pk = raw_pk.replace("\\\\n", "\n").replace("\\n", "\n").strip()
    
    creds_dict = {
        "type": "service_account",
        "project_id": "ringed-empire-508912-p6",
        "private_key_id": "da94d40dbcd4f54f79c1bdc7e67ea91f8afdf8ed",
        "private_key": cleaned_pk,
        "client_email": "devrim@ringed-empire-508912-p6.iam.gserviceaccount.com",
        "client_id": "112838976119952241535",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/devrim%40ringed-empire-508912-p6.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
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
