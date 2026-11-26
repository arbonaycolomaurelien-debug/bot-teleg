import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ==========================================
# CONFIGURATION DIRECTE
# ==========================================
TOKEN = "9275289835:AAHp9OKE_gOmUSTe2yG2Iqjyymtz8WnbWw0"

NOM = "Livraison à Amiens"
# Lien direct vers votre photo
PHOTO_URL = "https://i.postimg.cc/nc5RK9w0/dwibalzac80.png"

LOCALISATION = "Amiens et environs"
MESSAGE_ACCUEIL = "Bonjour ! Nous sommes disponibles sur Amiens, n'hésitez pas à consulter le menu ci-dessous !"

HORAIRES = """🕒 *NOS HORAIRES*
Disponible tous les jours de 10h00 à 01h00 du matin."""

SERVICES = """📋 *NOTRE MENU & SERVICES*
• Livraison rapide sur Amiens et alentours
• Produits sélectionnés avec soin
• Service discret et réactif"""

avis_clients = [5]

# ==========================================
# SERVEUR WEB (POUR RENDER)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot actif")
    def log_message(self, format, *args): pass

def lancer_serveur_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# ==========================================
# INTERFACE BOUTONS
# ==========================================
def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Consulter le menu", callback_data="menu")],
        [InlineKeyboardButton("🕒 Horaires", callback_data="horaires"),
         InlineKeyboardButton("📍 Zone de livraison", callback_data="localisation")],
        [InlineKeyboardButton("⭐ Avis clients", callback_data="avis")]
    ])

def bouton_retour():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour au menu", callback_data="retour")]])

# ==========================================
# LOGIQUE DU BOT
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=f"*{NOM}*\n\n{MESSAGE_ACCUEIL}",
        parse_mode="Markdown",
        reply_markup=menu_principal()
    )

async def gerer_boutons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choix = query.data

    if choix == "menu":
        await query.edit_message_media(
            media=InputMediaPhoto(media=PHOTO_URL, caption=SERVICES, parse_mode="Markdown"),
            reply_markup=bouton_retour()
        )
    elif choix == "horaires":
        await modifier_message(query, HORAIRES, bouton_retour())
    elif choix == "localisation":
        await modifier_message(query, f"📍 *ZONE DE LIVRAISON*\n\nNous livrons sur : {LOCALISATION}", bouton_retour())
    elif choix == "avis":
        moyenne = sum(avis_clients) / len(avis_clients)
        texte = f"⭐ *AVIS CLIENTS*\n\nNote : *{moyenne:.1f} / 5*\n\nLaissez une note :"
        keyboard = [
            [InlineKeyboardButton(f"⭐ {i}", callback_data=f"note_{i}") for i in range(1, 6)],
            [InlineKeyboardButton("⬅️ Retour", callback_data="retour")]
        ]
        await modifier_message(query, texte, InlineKeyboardMarkup(keyboard))
    elif choix.startswith("note_"):
        avis_clients.append(int(choix.split("_")[1]))
        await modifier_message(query, "✅ Merci pour votre note !", bouton_retour())
    elif choix == "retour":
        await query.edit_message_media(
            media=InputMediaPhoto(media=PHOTO_URL, caption=f"*{NOM}*\n\n{MESSAGE_ACCUEIL}", parse_mode="Markdown"),
            reply_markup=menu_principal()
        )

async def modifier_message(query, texte, clavier):
    await query.edit_message_caption(caption=texte, parse_mode="Markdown", reply_markup=clavier)

def main():
    # Lancement du serveur web
    threading.Thread(target=lancer_serveur_web, daemon=True).start()

    # Initialisation
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gerer_boutons))

    print("Bot démarré avec succès...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
