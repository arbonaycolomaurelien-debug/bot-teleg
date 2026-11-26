import os
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration du logging pour voir les erreurs dans les logs Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Récupération du Token
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Configuration des visuels et textes
NOM_BOT = "Livraison à Amiens"
# LIEN DIRECT VERS L'IMAGE (Important)
PHOTO_URL = "https://i.postimg.cc/sX97S6S8/menu.jpg"

MESSAGE_ACCUEIL = "Bonjour ! Nous sommes disponibles sur Amiens, n'hésitez pas à consulter le menu ci-dessous !"
HORAIRES = "🕒 *NOS HORAIRES*\nDisponible tous les jours de 10h00 à 01h00 du matin."
SERVICES = "📋 *NOTRE MENU & SERVICES*\n• Livraison rapide sur Amiens\n• Produits sélectionnés avec soin\n• Service discret et réactif"

# ==========================================
# SERVEUR DE SANTÉ (POUR RENDER)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    def log_message(self, format, *args): pass

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    httpd.serve_forever()

# ==========================================
# BOUTONS ET LOGIQUE
# ==========================================
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Consulter le menu", callback_data="view_menu")],
        [InlineKeyboardButton("🕒 Horaires", callback_data="view_hours"),
         InlineKeyboardButton("📍 Zone de livraison", callback_data="view_loc")],
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour au menu", callback_data="back_home")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=f"*{NOM_BOT}*\n\n{MESSAGE_ACCUEIL}",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "view_menu":
        await query.edit_message_caption(caption=SERVICES, parse_mode="Markdown", reply_markup=get_back_keyboard())
    
    elif data == "view_hours":
        await query.edit_message_caption(caption=HORAIRES, parse_mode="Markdown", reply_markup=get_back_keyboard())
    
    elif data == "view_loc":
        await query.edit_message_caption(caption="📍 Nous livrons sur Amiens et ses alentours.", parse_mode="Markdown", reply_markup=get_back_keyboard())
    
    elif data == "back_home":
        await query.edit_message_caption(caption=f"*{NOM_BOT}*\n\n{MESSAGE_ACCUEIL}", parse_mode="Markdown", reply_markup=get_main_keyboard())

# ==========================================
# LANCEMENT
# ==========================================
if __name__ == '__main__':
    if not TOKEN:
        print("Erreur : TELEGRAM_TOKEN non trouvé dans les variables d'environnement.")
    else:
        # Lancer le serveur web pour Render
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # Initialiser le bot
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_buttons))
        
        print("Le bot est démarré...")
        app.run_polling(drop_pending_updates=True)
