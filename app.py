import json
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- GOOGLE SHEETS BAĞLANTISI ---
def google_sheets_baglan():
    # Şifreyi Streamlit'in gizli kasasından okuyoruz
    creds_dict = json.loads(st.secrets["google_credentials"])
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Tablo ve sekme adını tam eşleştiriyoruz
    dosya = client.open("BIST_Trader_Arsivi")
    sekme = dosya.worksheet("Portfoy_Arsivi")
    return sekme

# --- STREAMLIT ARAYÜZÜ ---
st.title("BIST Trader - Portföy Girişi")

# Kullanıcıdan verileri alıyoruz
kullanici = st.text_input("Kullanıcı Adı", value="Devrim")
hisse = st.text_input("Varlık / Hisse Sembolü (Örn: GUMUS, THYAO)")
islem_turu = st.selectbox("İşlem Türü", ["ALIŞ", "SATIŞ"])
lot = st.number_input("Lot / Adet", min_value=0.0, format="%.2f")
fiyat = st.number_input("İşlem Fiyatı", min_value=0.0, format="%.2f")

# Kaydet Butonu
if st.button("İşlemi Kaydet"):
    if hisse and lot > 0 and fiyat > 0:
        try:
            # Bağlantıyı kur
            sekme = google_sheets_baglan()
            
            # Zaman damgası ve toplam tutar hesaplama
            zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            toplam_tutar = lot * fiyat
            
            # Veriyi listeye çevirip tabloya gönderiyoruz
            # Sıralama: A (Zaman), B (Kullanıcı), C (Hisse), D (Tür), E (Lot), F (Fiyat), G (Tutar)
            yeni_islem = [zaman, kullanici, hisse.upper(), islem_turu, lot, fiyat, toplam_tutar]
            sekme.append_row(yeni_islem)
            
            st.success(f"Başarılı! {hisse} işlemi Portfoy_Arsivi sekmesine kaydedildi.")
        
        except Exception as e:
            st.error(f"Bağlantı veya Kayıt Hatası: {e}")
    else:
        st.warning("Lütfen hisse sembolü, lot ve fiyat bilgilerini eksiksiz girin.")
