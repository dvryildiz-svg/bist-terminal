import os
import smtplib
from email.message import EmailMessage
from feedparser import parse

# GitHub Secrets'tan gelen verileri alıyoruz
ALICI_MAIL = os.environ.get("ALICI_MAIL")
GMAIL_USER = os.environ.get("MAIL_USER")
GMAIL_PASS = os.environ.get("MAIL_PASS")

# Takip edilecek BIST hisseleri listesi
HISSELER = ["SASA", "THYAO", "EREGL", "KCHOL", "GARAN"]


def bulten_olustur():
  rapor = "🤖 BİST Otomatik KAP ve Haber Bildirim Raporu\n\n"
  for hisse in HISSELER:
    url_kap = f"https://news.google.com/rss/search?q={hisse}+KAP+bildirimi+özel+durum&hl=TR&gl=TR&ceid=TR:tr"
    feed = parse(url_kap)

    rapor += f"📌 HİSSE: {hisse}\n"
    if feed.entries:
      for entry in feed.entries[:2]:  # Son 2 bildirim
        zaman = getattr(entry, "published", "Güncel")
        rapor += f" - [{zaman}] {entry.title}\n   {entry.link}\n"
    else:
      rapor += " - Son dönemde yeni KAP bildirimi bulunamadı.\n"
    rapor += "-" * 40 + "\n"
  return rapor


def mail_gonder(icerik):
  if not GMAIL_USER or not GMAIL_PASS or not ALICI_MAIL:
    print("Mail bilgileri veya alıcı eksik!")
    return

  msg = EmailMessage()
  msg["Subject"] = "🔔 Günlük BİST & KAP Otomatik Bildirim Raporu"
  msg["From"] = GMAIL_USER
  msg["To"] = ALICI_MAIL  # Birden fazla adresi virgülle destekler
  msg.set_content(icerik)

  try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
      server.login(GMAIL_USER, GMAIL_PASS)
      server.send_message(msg)
    print("E-posta başarıyla gönderildi!")
  except Exception as e:
    print(f"Mail gönderilemedi: {e}")


if __name__ == "__main__":
  rapor_metni = bulten_olustur()
  mail_gonder(rapor_metni)
