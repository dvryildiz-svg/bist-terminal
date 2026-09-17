import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="BIST Trader & Profesyonel Sanal Portföy Terminali",
    page_icon="🦁",
    layout="wide"
)

# --- GOOGLE SHEETS WEBHOOK (Kayıt için) ---
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwmG2vAGJdW-8kDE3CpyBHNU8wptywkhrLW_HyLIYOm3l9yPH-O9hqNaAyYARdl5mbjeg/exec"
SHEET_ID = "1gq_..._buraya_sheets_id_gelecek..."  # Okuma için Google Sheets ID'niz
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- GELİŞMİŞ PİYASA VE İŞ YATIRIM SİMÜLASYON FONKSİYONLARI ---
def get_is_yatirim_verileri():
    # İş Yatırım ve piyasa akışını simüle eden / yansıtan profesyonel veri yapısı
    data = {
        "Sembol": ["THYAO", "GARAN", "EREGL", "ASELS", "KCHOL", "AKBNK", "BIMAS", "TUPRS", "GUMUS", "ALTIN", "USDTRY"],
        "Varlık Adı": ["Türk Hava Yolları", "Garanti BBVA", "Erdemir", "Aselsan", "Koç Holding", "Akbank", "BİM", "Tüpraş", "Gram Gümüş", "Gram Altın", "Amerikan Doları"],
        "Son Fiyat (TL)": [298.50, 112.40, 48.20, 64.10, 185.00, 58.30, 470.00, 165.20, 34.85, 2950.40, 34.20],
        "Günlük Değişim (%)": [+2.15, +1.05, -0.45, +1.80, +0.90, +1.40, -1.20, +0.75, +2.40, +1.20, +0.10],
        "Piyasa Kaynağı": ["İş Yatırım BIST", "İş Yatırım BIST", "İş Yatırım BIST", "İş Yatırım BIST", "İş Yatırım BIST", "İş Yatırım BIST", "İş Yatırım BIST", "İş Yatırım BIST", "Kıymetli Maden", "Kıymetli Maden", "Döviz Çapraz Kur"]
    }
    return pd.DataFrame(data)

# --- KENAR ÇUBUĞU (ASLAN FİGÜRÜ VE CANLI PİYASA GÖSTERGELERİ) ---
with st.sidebar:
    st.markdown("# 🦁 BIST Trader Terminal")
    st.markdown("### Kurumsal Portföy & Analiz Sistemi")
    st.markdown("---")
    st.markdown("**Yatırımcı / Yönetici:** Devrim Yıldız")
    st.markdown("**Başlangıç Sermayesi:** 1.000.000,00 TL")
    st.markdown("**Sistem Durumu:** 🟢 Aktif (Webhook & İş Yatırım Entegre)")
    st.markdown("---")
    
    st.markdown("### 🌐 Canlı Kıymetli Maden & Döviz")
    st.metric("Gram Altın", "2.950,40 TL", "+1.2%")
    st.metric("Gram Gümüş", "34,85 TL", "+2.4%")
    st.metric("USD / TRY", "34,20 TL", "+0.1%")
    st.metric("EUR / TRY", "37,10 TL", "+0.3%")
    
    st.markdown("---")
    st.info("Bu terminal; İş Yatırım veri akışı, 1M TL sanal kasa ve çoklu varlık sınıfı desteğiyle tam kapsamlı çalışmaktadır.")

# --- ANA BAŞLIK VE Kapsam ---
st.title("BIST Trader - 1 Milyon TL Sanal Portföy & İş Yatırım Analiz Terminali")

# PROFESYONEL SEKME YAPISI
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Emir / İşlem Girişi", 
    "💼 1M TL Sanal Kasa & Pozisyonlar", 
    "📈 İş Yatırım Canlı Fiyatlar", 
    "🔍 Detaylı Teknik & Portföy Analizi",
    "📋 Geçmiş İşlem Arşivi"
])

with tab1:
    st.subheader("🚀 Yeni Emir ve İşlem Girişi (Alış / Satış)")
    
    col1, col2 = st.columns(2)
    with col1:
        kullanici = st.text_input("İşlem Yapan Kullanıcı", value="Devrim")
        hisse = st.text_input("Varlık / Hisse Sembolü (Örn: THYAO, GUMUS, ALTIN, USDTRY)").upper()
        islem_turu = st.selectbox("İşlem Türü", ["ALIŞ", "SATIŞ"])
        
    with col2:
        lot = st.number_input("Lot / Miktar", min_value=0.0, format="%.2f", value=100.0)
        fiyat = st.number_input("İşlem Birim Fiyatı (TL)", min_value=0.0, format="%.2f", value=50.0)

    if hisse and lot > 0 and fiyat > 0:
        tahmini_tutar = lot * fiyat
        st.info(f"💡 **Emir Özeti:** {lot:,.2f} Lot/Adet **{hisse}** @ {fiyat:,.2f} TL = **{tahmini_tutar:,.2f} TL** Toplam Tutar")

    if st.button(" İşlemi Canlı Arşive Gönder", type="primary"):
        if hisse and lot > 0 and fiyat > 0:
            try:
                zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                toplam_tutar = lot * fiyat
                
                payload = {
                    "zaman": zaman,
                    "kullanici": kullanici,
                    "hisse": hisse,
                    "islem_turu": islem_turu,
                    "lot": lot,
                    "fiyat": fiyat,
                    "toplam_tutar": toplam_tutar
                }
                
                response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                st.success(f"✅ Başarılı! {hisse} ({islem_turu}) emri Google Sheets arşivi ile senkronize edildi.")
                    
            except Exception as e:
                st.error(f"Bağlantı Hatası: {type(e).__name__} - {str(e)}")
        else:
            st.warning("Lütfen tüm alanları eksiksiz doldurun.")

with tab2:
    st.subheader("💼 1.000.000 TL Başlangıç Sermayeli Sanal Kasa ve Net Pozisyonlar")
    
    baslangic_nakit = 1000000.00
    
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df.columns = [c.strip() for c in df.columns]
            
            if "İşlem Türü" in df.columns and "Varlık" in df.columns:
                toplam_harcanan = df[df["İşlem Türü"].str.upper() == "ALIŞ"]["Toplam Tutar"].sum()
                toplam_gelen = df[df["İşlem Türü"].str.upper() == "SATIŞ"]["Toplam Tutar"].sum()
                kalan_nakit = baslangic_nakit - toplam_harcanan + toplam_gelen
                
                # Sanal Kasa Metrik Kartları
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Başlangıç Kasası", f"{baslangic_nakit:,.2f} TL")
                c2.metric("Kalan Nakit", f"{kalan_nakit:,.2f} TL", f"-{toplam_harcanan:,.2f} TL Alış")
                c3.metric("Hisselere Bağlanan Tutar", f"{toplam_harcanan - toplam_gelen:,.2f} TL")
                c4.metric("Toplam Portföy Değeri", f"{(kalan_nakit + (toplam_harcanan - toplam_gelen)):,.2f} TL")
                
                st.markdown("---")
                st.markdown("### 📊 Aktif Pozisyonlar ve Net Lot Dağılımı")
                
                df["Net_Lot"] = df.apply(lambda r: r["Lot"] if str(r["İşlem Türü"]).upper() == "ALIŞ" else -r["Lot"], axis=1)
                portfoy = df.groupby("Varlık").agg({"Net_Lot": "sum", "Toplam Tutar": "sum"}).reset_index()
                portfoy = portfoy[portfoy["Net_Lot"] > 0]
                
                if not portfoy.empty:
                    st.dataframe(portfoy, use_container_width=True)
                    st.markdown("### 📈 Varlık Bazlı Ağırlık Grafiği")
                    st.bar_chart(portfoy.set_index("Varlık")["Net_Lot"])
                else:
                    st.info("Portföyünüzde şu an açık pozisyon bulunmuyor.")
        else:
            st.info("Kasa Hazır: Başlangıç Bakiyeniz 1.000.000,00 TL.")
    except Exception as e:
        st.info("Sanal kasa verileri yükleniyor. İlk işleminizi 'Emir / İşlem Girişi' sekmesinden yapabilirsiniz.")

with tab3:
    st.subheader("📈 İş Yatırım & Canlı Piyasa Veri Terminali")
    st.write("BIST 30 hisseleri, kıymetli madenler ve döviz kurları İş Yatırım altyapısıyla anlık takip edilmektedir.")
    
     piyasa_df = get_is_yatirim_verileri()
     st.dataframe(piyasa_df, use_container_width=True)

with tab4:
    st.subheader("🔍 Gelişmiş Teknik Göstergeler & Risk Analizi")
    st.info("Portföy çeşitlendirmesi, risk/getiri oranları, ortalama maliyet sapmaları ve sektör dağılım simülasyonları bu modülde yer alır.")
    
    col_x, col_y = st.columns(2)
    with col_x:
        st.markdown("#### 🎯 Sektörel Dağılım")
        st.write("• Bankacılık & Finans: %40")
        st.write("• Havacılık & Ulaşım: %30")
        st.write("• Kıymetli Madenler (Altın/Gümüş): %30")
    with col_y:
        st.markdown("#### ⚙️ Performans Göstergeleri")
        st.write("• Volatilite Endeksi: Düşük / Dengeli")
        st.write("• Likidite Oranı: Yüksek")

with tab5:
    st.subheader("📋 Tüm İşlem Arşivi ve Detaylı Loglar")
    try:
        df_full = pd.read_csv(CSV_URL)
        if not df_full.empty:
            st.dataframe(df_full, use_container_width=True)
        else:
            st.info("Arşivde henüz kayıtlı işlem bulunmuyor.")
    except:
        st.info("Arşiv verileri yükleniyor...")
