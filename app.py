import json
import streamlit as st
import gspread
from datetime import datetime

# --- GOOGLE SHEETS BAĞLANTISI ---
def google_sheets_baglan():
    creds_dict = json.loads(st.secrets["google_credentials"])
    
    # --- KABA KUVVET FİLTRESİ ---
    pk = creds_dict.get("private_key", "")
    pk = pk.replace("\\n", "\n")
    
    # İlk tireyi (-) bul ve ondan önceki her şeyi (nokta, boşluk vb.) kesip at.
    if "-" in pk:
        ilk_tire = pk.find("-")
        pk = pk[ilk_tire:]
        
    creds_dict["private_key"] = pk
    # ----------------------------------
    
    # Hata durumunda düşmanı görebilmek için şifrenin ilk 15 karakterini kaydediyoruz
    st.session_state["debug_pk"] = pk[:15] 
    
    client = gspread.service_account_from_dict(creds_dict)
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
            # Bağlantıyı kur
            sekme = google_sheets_baglan()
            
            # Zaman damgası ve toplam tutar hesaplama
            zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            toplam_tutar = lot * fiyat
            
            # Veriyi listeye çevirip tabloya gönderiyoruz
            yeni_islem = [zaman, kullanici, hisse.upper(), islem_turu, lot, fiyat, toplam_tutar]
            sekme.append_row(yeni_islem)
            
            st.success(f"Başarılı! {hisse} işlemi Portfoy_Arsivi sekmesine kaydedildi.")
            
        except Exception as e:
            # Hata verirse radarı ekrana basıyoruz
            debug_bilgisi = st.session_state.get("debug_pk", "Okunamadı")
            st.error(f"Hata: {str(e)}")
            st.warning(f"RADAR (Sistemin gördüğü şifre başlangıcı): {repr(debug_bilgisi)}")
    else:
        st.warning("Lütfen hisse sembolü, lot ve fiyat bilgilerini eksiksiz girin.")
