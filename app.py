import json
import tempfile
import os
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- GOOGLE SHEETS BAĞLANTISI (GEÇİCİ DOSYA YÖNTEMİ) ---
def google_sheets_baglan():
    # Secrets kasasından veriyi sözlük olarak alıyoruz (İster JSON string ister TOML olsun çalışır)
    try:
        if "google_credentials" in st.secrets:
            creds_dict = json.loads(st.secrets["google_credentials"])
        else:
            creds_dict = dict(st.secrets["gcp_service_account"])
    except Exception:
        creds_dict = dict(st.secrets["gcp_service_account"])

    # Veriyi sunucuda anlık olarak fiziksel bir JSON dosyasına yazıyoruz
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(creds_dict, f)
        temp_filename = f.name

    try:
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Google, dosyayı doğrudan okuduğu için PEM veya padding hatası asla vermez
        creds = Credentials.from_service_account_file(temp_filename, scopes=scopes)
        client = gspread.authorize(creds)
        
        dosya = client.open("BIST_Trader_Arsivi")
        sekme = dosya.worksheet("Portfoy_Arsivi")
        return sekme
        
    finally:
        # İşlem bitince geçici dosyayı güvenle temizliyoruz
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
