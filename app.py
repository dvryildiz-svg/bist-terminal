import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- GOOGLE SHEETS BAĞLANTISI ---
def google_sheets_baglan():
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # --- YER TUTUCU VE NOKTA TEMİZLEME FİLTRESİ ---
    pk = creds_dict.get("private_key", "")
    
    # Yer tutucu olarak kalmış olabilecek tüm üç noktaları (...) ve yabancı noktaları temizliyoruz
    pk = pk.replace("...", "").replace("..", "")
    
    # Satır sonlarını düzenle
    pk = pk.replace("\\n", "\n").strip()
    creds_dict["private_key"] = pk
    # -----------------------------------------------
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    dosya = client.open("BIST_Trader_Arsivi")
    sekme = dosya.worksheet("Portfoy_Arsivi")
    return sekme

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
