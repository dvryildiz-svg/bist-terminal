import json
import streamlit as st
import gspread
import re
from datetime import datetime

# --- GOOGLE SHEETS BAĞLANTISI ---
def google_sheets_baglan():
    creds_dict = json.loads(st.secrets["google_credentials"])
    pk = creds_dict.get("private_key", "")
    
    # --- DNA YENİLEYİCİ FİLTRE ---
    # 1. Şifrenin sadece gövdesini (BEGIN ve END arasını) cımbızla alıyoruz
    match = re.search(r"-----BEGIN PRIVATE KEY-----(.*?)-----END PRIVATE KEY-----", pk, re.DOTALL)
    if match:
        govde = match.group(1)
        
        # 2. Gövdeye sızmış olan nokta (.), boşluk veya alt satır gibi tüm geçersiz karakterleri yok et
        # (Sadece geçerli şifre karakterleri olan harf, rakam, + ve / işaretleri kalır)
        govde = re.sub(r'[^A-Za-z0-9+/=]', '', govde)
        
        # 3. Google'ın standartlarına tam uygun olması için şifreyi 64 karakterlik nizami satırlara böl
        satirlar = [govde[i:i+64] for i in range(0, len(govde), 64)]
        
        # 4. Şifreyi tertemiz bir şekilde baştan inşa edip sisteme geri koy
        yeni_pk = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(satirlar) + "\n-----END PRIVATE KEY-----\n"
        creds_dict["private_key"] = yeni_pk
    # -----------------------------
    
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
            st.error(f"Hata: {str(e)}")
    else:
        st.warning("Lütfen hisse sembolü, lot ve fiyat bilgilerini eksiksiz girin.")
