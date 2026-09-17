import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="BIST Trader Terminal",
    page_icon="🦁",
    layout="wide"
)

# --- GOOGLE SHEETS WEBHOOK & CSV BAĞLANTILARI ---
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwmG2vAGJdW-8kDE3CpyBHNU8wptywkhrLW_HyLIYOm3l9yPH-O9hqNaAyYARdl5mbjeg/exec"

# Google Sheets Dosya ID'nizi buraya yazabilirsiniz (Okuma için)
# (Örnek: https://docs.google.com/spreadsheets/d/BURADAKI_ID_OLACAK/edit)
SHEET_ID = "1gq_..._buraya_sheets_id_gelecek..." 
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- KENAR ÇUCUĞU (ASLAN FİGÜRÜ VE TERMİNAL BİLGİSİ) ---
with st.sidebar:
    st.markdown("# 🦁 BIST Trader")
    st.markdown("### Profesyonel Portföy & Analiz Terminali")
    st.markdown("---")
    st.markdown("**Yatırımcı:** Devrim Yıldız")
    st.markdown("**Sistem Durumu:** 🟢 Aktif (Webhook Bağlı)")
    st.markdown("---")
    st.info("Piyasa verileri, işlem geçmişi ve sanal portföy dağılımı anlık olarak senkronize edilmektedir.")

# --- ANA BAŞLIK ---
st.title("BIST Trader - Portföy ve Analiz Terminali")

# SEKME YAPISI
tab1, tab2, tab3 = st.tabs(["📊 İşlem Girişi & Kayıt", "📈 Sanal Portföy & Dağılım", "📋 Toplu Analiz & Geçmiş"])

with tab1:
    st.subheader("Yeni İşlem Girişi")
    
    col1, col2 = st.columns(2)
    with col1:
        kullanici = st.text_input("Kullanıcı Adı", value="Devrim")
        hisse = st.text_input("Varlık / Hisse Sembolü (Örn: GUMUS, THYAO, EREGL)")
        islem_turu = st.selectbox("İşlem Türü", ["ALIŞ", "SATIŞ"])
        
    with col2:
        lot = st.number_input("Lot / Adet", min_value=0.0, format="%.2f", value=1.0)
        fiyat = st.number_input("İşlem Fiyatı (TL)", min_value=0.0, format="%.2f", value=100.0)

    # Özet Bilgi Kartı
    if hisse and lot > 0 and fiyat > 0:
        tahmini_tutar = lot * fiyat
        st.info(f"💡 **İşlem Özeti:** {lot:,.2f} Lot {hisse.upper()} @ {fiyat:,.2f} TL = **{tahmini_tutar:,.2f} TL** Toplam Tutar")

    if st.button(" İşlemi Arşive Kaydet", type="primary"):
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
                    st.success(f" Başarılı! {hisse.upper()} ({islem_turu}) işlemi arşive kaydedildi.")
                else:
                    st.error(f"Kayıt Hatası: {result.get('message', 'Bilinmeyen hata')}")
                    
            except Exception as e:
                st.error(f"Bağlantı Hatası: {type(e).__name__} - {str(e)}")
        else:
            st.warning("Lütfen tüm alanları eksiksiz doldurun.")

with tab2:
    st.subheader("Sanal Portföy ve Varlık Dağılım Grafikleri")
    
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            # Sütun isimleri esnekliği için temizlik
            df.columns = [c.strip() for c in df.columns]
            
            # Üst İstatistik Kartları
            toplam_islem = len(df)
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Toplam İşlem Adedi", f"{toplam_islem} Adet")
            
            # Varlık Bazlı Sanal Portföy Hesaplama
            if "İşlem Türü" in df.columns and "Varlık" in df.columns:
                # Alışları pozitif, satışları negatif alarak net lot hesaplama
                df["Net_Lot"] = df.apply(lambda r: r["Lot"] if str(r["İşlem Türü"]).upper() == "ALIŞ" else -r["Lot"], axis=1)
                portfoy = df.groupby("Varlık").agg({"Net_Lot": "sum", "Toplam Tutar": "sum"}).reset_index()
                portfoy = portfoy[portfoy["Net_Lot"] > 0]
                
                col_b.metric("Aktif Varlık Çeşidi", f"{len(portfoy)} Farklı Hisse/Varlık")
                
                if not portfoy.empty:
                    st.markdown("---")
                    st.markdown("### 💼 Aktif Portföy Dağılım Tablosu")
                    st.dataframe(portfoy, use_container_width=True)
                    
                    st.markdown("### 📊 Varlık Bazlı Lot Dağılım Grafiği")
                    st.bar_chart(portfoy.set_index("Varlık")["Net_Lot"])
                else:
                    st.warning("Portföyünüzde şu an aktif varlık bulunmuyor (Tüm varlıklar satılmış olabilir).")
        else:
            st.info("Arşivde henüz veri bulunmuyor.")
    except Exception as e:
        st.info("📊 Portföy verileri yükleniyor veya Google Sheets CSV bağlantısı bekleniyor. (İlk kayıt eklendiğinde grafikler otomatik aktifleşecektir).")

with tab3:
    st.subheader("📋 Toplu Analiz ve Tüm İşlem Geçmişi")
    try:
        df_full = pd.read_csv(CSV_URL)
        if not df_full.empty:
            st.dataframe(df_full, use_container_width=True)
            
            # Toplu Özet Metrikleri
            st.markdown("---")
            st.markdown("### 📈 Genel Piyasa ve İşlem İstatistikleri")
            st.write(f"Sistemde kayıtlı toplam **{len(df_full)}** adet işlem hareketi incelenmektedir.")
        else:
            st.info("Henüz geçmiş işlem kaydı mevcut değil.")
    except Exception as e:
        st.info("Geçmiş işlem dökümü yükleniyor...")
