import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import re

# --- GOOGLE SHEETS BAĞLANTISI ---
def google_sheets_baglan():
    creds_dict = json.loads(st.secrets["google_credentials"])
    pk = creds_dict.get("private_key", "")
    
    # --- MATEMATİKSEL KUSURSUZLUĞUNDA PADDING VE GÖVDE DÜZENLEYİCİ ---
    match = re.search(r"-----BEGIN PRIVATE KEY-----(.*?)-----END PRIVATE KEY-----", pk, re.DOTALL)
    if match:
        raw_body = match.group(1)
        
        # 1. Tüm boşlukları, yeni satırları, noktaları ve geçersiz karakterleri temizle
        clean_body = re.sub(r'[^A-Za-z0-9+/=]', '', raw_body)
        
        # 2. Mevcut dolgu (=) işaretlerini temizleyip uzunluğu tabana göre yeniden hesapla
        clean_body = clean_body.rstrip('=')
        padding_needed = len(clean_body) % 4
        if padding_needed:
            clean_body += '=' * (4 - padding_needed)
            
        # 3. Standartlara tam uygun olması için 64 karakterlik satırlar halinde böl
        lines = [clean_body[i:i+64] for i in range(0, len(clean_body), 64)]
        
        # 4. Saf ve hatasız PEM anahtarını yeniden inşa et
        pk = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(lines) + "\n-----END PRIVATE KEY-----\n"
        creds_dict["private_key"] = pk
    # -------------------------------------------------------------
    
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
