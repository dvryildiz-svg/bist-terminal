import os
import smtplib
from email.message import EmailMessage
from feedparser import parse
from isyatirimhisse import fetch_stock_data
import pandas as pd

ALICI_MAIL = os.environ.get("ALICI_MAIL")
GMAIL_USER = os.environ.get("MAIL_USER")
GMAIL_PASS = os.environ.get("MAIL_PASS")

HISSELER = ["SASA", "THYAO", "EREGL", "KCHOL", "GARAN"]


def analiz_uret_ve_bulten_hazirla():
  rapor = (
      "🤖 BİST Akıllı Karar Destek & Otomatik Bildirim Raporu\n"
      "=" * 55
      + "\n\n"
  )

  for hisse in HISSELER:
    rapor += f"📌 HİSSE: {hisse}\n"
    try:
      # Teknik ve Haber Verisi Çekimi
      bitis = pd.Timestamp.now().strftime("%d-%m-%Y")
      baslangic = (pd.Timestamp.now() - pd.Timedelta(days=120)).strftime(
          "%d-%m-%Y"
      )
      df = fetch_stock_data(
          symbols=[hisse], start_date=baslangic, end_date=bitis
      )

      if df is not None and not df.empty:
        df.columns = [str(col).upper() for col in df.columns]
        k_col = next(
            (c for c in df.columns if "KAP" in c or "CLOSE" in c or "FIYAT" in c),
            None,
        )
        t_col = next((c for c in df.columns if "TARIH" in c or "DATE" in c), None)

        if k_col and t_col:
          df["Kapanis"] = pd.to_numeric(df[k_col], errors="coerce")
          son_fiyat = df["Kapanis"].iloc[-1]

          # Basit İndikatör Kontrolü
          sma50 = df["Kapanis"].rolling(window=min(30, len(df))).mean().iloc[-1]
          delta = df["Kapanis"].diff()
          gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
          loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
          rs = gain / loss
          rsi = 100 - (100 / (1 + rs))
          son_rsi = rsi.iloc[-1] if not rsi.empty else 50

          # Haber ve KAP duygu taraması
          url_kap = f"https://news.google.com/rss/search?q={hisse}+KAP+bildirimi+özel+durum&hl=TR&gl=TR&ceid=TR:tr"
          feed = parse(url_kap)

          haber_skoru = 0
          olumlu = [
              "sözleşme",
              "ihale",
              "kar",
              "rekor",
              "artış",
              "onay",
              "yatırım",
          ]
          olumsuz = ["zarar", "ceza", "soruşturma", "dava", "borç", "düşüş"]

          bildirim_metinleri = []
          if feed.entries:
            for entry in feed.entries[:2]:
              bildirim_metinleri.append(entry.title)
              baslik_lower = entry.title.lower()
              for o in olumlu:
                if o in baslik_lower:
                  haber_skoru += 1
              for ol in olumsuz:
                if ol in baslik_lower:
                  haber_skoru -= 1

          # Sinyal Kararı
          puan = 0
          if son_rsi < 35:
            puan += 1
          if son_rsi > 65:
            puan -= 1
          if son_fiyat > sma50:
            puan += 1
          else:
            puan -= 1
          puan += haber_skoru

          if puan >= 2:
            karar = "AL"
          elif puan <= -1:
            karar = "SAT"
          else:
            karar = "TUT (NÖTR)"

          rapor += f" - Fiyat: {son_fiyat:.2f} TL | RSI: {son_rsi:.1f}\n"
          rapor += f" - Karar Önerisi: [{karar}]\n"
          rapor += f" - Son Gelişmeler / Bildirimler:\n"
          if bildirim_metinleri:
            for b in bildirim_metinleri:
              rapor += f"   * {b}\n"
          else:
            rapor += "   * Yakın zamanda yeni KAP bildirimi bulunamadı.\n"
        else:
          rapor += " - Teknik veri sütunları işlenemedi.\n"
      else:
        rapor += " - Fiyat verisi alınamadı.\n"
    except Exception as e:
      rapor += f" - Analiz sırasında hata oluştu.\n"

    rapor += "-" * 50 + "\n"

  return rapor


def mail_gonder(icerik):
  if not GMAIL_USER or not GMAIL_PASS or not ALICI_MAIL:
    print("Mail bilgileri veya alıcı eksik!")
    return

  msg = EmailMessage()
  msg["Subject"] = "🔔 Günlük BİST Akıllı Karar & KAP Bildirim Raporu"
  msg["From"] = GMAIL_USER
  msg["To"] = ALICI_MAIL
  msg.set_content(icerik)

  try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
      server.login(GMAIL_USER, GMAIL_PASS)
      server.send_message(msg)
    print("E-posta başarıyla gönderildi!")
  except Exception as e:
    print(f"Mail gönderilemedi: {e}")


if __name__ == "__main__":
  rapor_metni = analiz_uret_ve_bulten_hazirla()
  mail_gonder(rapor_metni)
