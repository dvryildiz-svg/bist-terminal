import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="BIST Trader Terminal", layout="wide")

st.title("BIST Trader - Portföy ve Analiz Terminali")

# Google Apps Script Webhook URL'niz (Kayıt için)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwmG2vAGJdW-8kDE3CpyBHNU8wptywkhrLW_HyLIYOm3l9yPH-O9hqNaAyYARdl5mbjeg/exec"

# Google Sheets CSV Okuma Bağlantısı (Analiz ve Sanal Portföy için)
# (Not: Google Sheets dosyanızın "Bağlantıya sahip herkes okuyabilir" şeklinde paylaşılmış olması gerekir)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1gq_..._buraya_dosya_id_gelecek .../export?format=csv&sheet=Portfoy_Arsivi"

tab1, tab2 = st.tabs(["📊 İşlem Girişi & Özet", "📈 Sanal Portföy & Analiz"])

with tab1:
    st.subheader("Yeni İşlem Kaydı")
    
    col1, col2 = st.columns(2)
    with col1:
        kullanici = st.text_input("Kullanıcı Adı", value="Devrim")
        hisse = st.text_input("Varlık / Hisse Sembolü (Örn: GUMUS, THYAO)")
        islem_turu = st.selectbox("İşlem Türü", ["ALIŞ", "SATIŞ"])
        
    with col2:
        lot = st.number_input("Lot / Adet", min_value=0.0, format="%.2f", value=1.0)
        fiyat = st.number_input("İşlem Fiyatı", min_value=0.0, format="%.2f", value=100.0)

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
                
                response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                result = response.json()
                
                if result.get("status") == "success":
                    st.success(f"Başarılı! {hisse.upper()} işlemi arşive kaydedildi.")
                else:
                    st.error(f"Kayıt Hatası: {result.get('message', 'Bilinmeyen hata')}")
                    
            except Exception as e:
                st.error(f"Bağlantı Hatası: {type(e).__name__} - {str(e)}")
        else:
            st.warning("Lütfen tüm alanları eksiksiz doldurun.")

with tab2:
    st.subheader("Sanal Portföy ve Varlık Dağılımı")
    
    # Verileri Google Sheets'ten çekme denemesi
    try:
        # Doğrudan Google Sheets dosya ID'ni buraya yazarak CSV olarak okuyoruz
        # Örnek CSV export linki yapısı: https://docs.google.com/spreadsheets/d/DOSYA_ID/export?format=csv&gid=SEKME_GID
        sheet_id = "1gq_... (Google Sheets ID'niz)" 
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        df = pd.read_csv(csv_url)
        
        if not df.empty:
            st.markdown("### 📋 Tüm İşlem Geçmişi")
            st.dataframe(df, use_container_width=True)
            
            # Sanal Portföy Hesaplama (Özet Tablo)
            st.markdown("### 💼 Anlık Varlık Durumu (Sanal Portföy)")
            
            # Alış ve satışları netleştirerek basit bir portföy özeti çıkarıyoruz
            # Not: Tablonuzdaki sütun isimlerinin sırasına göre uyarlanmıştır
            if "İşlem Türü" in df.columns and "Varlık" in df.columns:
                # Basit bir netleştirme mantığı
                df["Net_Lot"] = df.apply(lambda row: row["Lot"] if row["İşlem Türü"] == "ALIŞ" else -row["Lot"], axis=1)
                portfoy_ozet = df.groupby("Varlık").agg({"Net_Lot": "sum", "Toplam Tutar": "sum"}).reset_index()
                portfoy_ozet = portfoy_ozet[portfoy_ozet["Net_Lot"] > 0] # Sadece eldekiler
                
                st.dataframe(portfoy_ozet, use_container_width=True)
                
                # Grafik
                if not portfoy_ozet.empty:
                    st.bar_chart(portfoy_ozet.set_index("Varlık")["Net_Lot"])
        else:
            st.info("Henüz arşivde kayıtlı işlem bulunmuyor. İlk işlemini 'İşlem Girişi' sekmesinden ekleyebilirsin.")
            
    except Exception as e:
        st.warning("Portföy verileri yüklenirken bağlantı bekleniyor. Google Sheets dosyanızın paylaşım ayarlarının 'Bağlantıya sahip herkes okuyabilir' olduğundan emin olun.")
        st.info(f"Teknik Detay: {str(e)}")
