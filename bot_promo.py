py
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# TOKEN DIRECT (Utilisez les variables d'environnement sur Render pour plus de sécurité)
TOKEN = "9275289835:AAHp9OKE_gOmUSTe2yG2Iqjyymtz8WnbWw0"

# RÉGLAGES
NOM = "Livraison à Amiens"
PHOTO_URL = "https://i.postimg.cc/sX97S6S8/menu.jpg"
LOCALISATION = "Amiens et environs"
MESSAGE_ACCUEIL = "Bonjour ! Nous sommes disponibles sur Amiens, n'hésitez pas à consulter le menu ci-dessous !"
HORAIRES = "🕒 *NOS HORAIRES*\nDisponible tous les jours de 10h00 à 01h00 du matin."
SERVICES = "📋 *NOTRE MENU & SERVICES*\n• Livraison rapide sur Amiens\n• Produits sélectionnés\n• Service discret"

avis_clients = [5]

# SERVEUR POUR RENDER
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args): pass

def lancer_serveur():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

# INTERFACE
def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Consulter le menu", callback_data="menu")],
        [InlineKeyboardButton("🕒 Horaires", callback_data="horaires"),
         InlineKeyboardButton("📍 Zone de livraison", callback_data="localisation")],
        [InlineKeyboardButton("⭐ Avis clients", callback_data="avis")]
    ])

def bouton_retour():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="retour")]])

# LOGIQUE
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(photo=PHOTO_URL, caption=f"*{NOM}*\n\n{MESSAGE_ACCUEIL}", parse_mode="Markdown", reply_markup=menu_principal())

async def gerer_boutons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choix = query.data

    if choix == "menu":
        await query.edit_message_media(media=InputMediaPhoto(media=PHOTO_URL, caption=SERVICES, parse_mode="Markdown"), reply_markup=bouton_retour())
    elif choix == "horaires":
        await query.edit_message_caption(caption=HORAIRES, parse_mode="Markdown", reply_markup=bouton_retour())
    elif choix == "localisation":
        await query.edit_message_caption(caption=f"📍 *ZONE DE LIVRAISON*\n\n{LOCALISATION}", parse_mode="Markdown", reply_markup=bouton_retour())
    elif choix == "avis":
        moyenne = sum(avis_clients) / len(avis_clients)
        texte = f"⭐ *AVIS CLIENTS*\n\nNote : *{moyenne:.1f}/5*\n\nLaissez une note :"
        clavier = InlineKeyboardMarkup([[InlineKeyboardButton(f"⭐ {i}", callback_data=f"note_{i}") for i in range(1, 6)], [InlineKeyboardButton("⬅️ Retour", callback_data="retour")]])
        await query.edit_message_caption(caption=texte, parse_mode="Markdown", reply_markup=clavier)
    elif choix.startswith("note_"):
        avis_clients.append(int(choix.split("_")[1]))
        await query.edit_message_caption(caption="✅ Merci pour votre note !", parse_mode="Markdown", reply_markup=bouton_retour())
    elif choix == "retour":
        await query.edit_message_media(media=InputMediaPhoto(media=PHOTO_URL, caption=f"*{NOM}*\n\n{MESSAGE_ACCUEIL}", parse_mode="Markdown"), reply_markup=menu_principal())

def main():
    threading.Thread(target=lancer_serveur, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gerer_boutons))
    print("Bot en ligne...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
