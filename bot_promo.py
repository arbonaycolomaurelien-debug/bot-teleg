
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import schedule

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
PHOTO_URL = os.environ.get("PHOTO_URL", "")
WHATSAPP_URL = os.environ.get("WHATSAPP_URL", "")
CAPTION = os.environ.get("PROMO_CAPTION", "Offre spéciale du vendredi !")
BUTTON_TEXT = os.environ.get("BUTTON_TEXT", "Contacter sur WhatsApp")
SEND_TIME = os.environ.get("SEND_TIME", "09:00")


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot actif")

    def log_message(self, format, *args):
        return


def start_web_server():
    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


def envoyer_promo_vendredi():
    if not all([TELEGRAM_TOKEN, CHAT_ID, PHOTO_URL, WHATSAPP_URL]):
        print("Variables manquantes : vérifiez TELEGRAM_TOKEN, CHAT_ID, PHOTO_URL et WHATSAPP_URL.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    reply_markup = {
        "inline_keyboard": [
            [{"text": BUTTON_TEXT, "url": WHATSAPP_URL}]
        ]
    }
    payload = {
        "chat_id": CHAT_ID,
        "photo": PHOTO_URL,
        "caption": CAPTION,
        "reply_markup": str(reply_markup).replace("'", '"'),
    }
    response = requests.post(url, data=payload, timeout=30)
    print("Envoi Telegram :", response.status_code, response.text)


if name == "main":
    threading.Thread(target=start_web_server, daemon=True).start()
    schedule.every().friday.at(SEND_TIME).do(envoyer_promo_vendredi)
    print(f"Bot démarré. Envoi prévu chaque vendredi à {SEND_TIME}.")

    while True:
        schedule.run_pending()
        time.sleep(30)
