import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ==========================================
# VOS RÉGLAGES PERSONNALISÉS
# ==========================================
NOM = "Livraison à Amiens"
PHOTO_ACCUEIL = "menu.jpg"  # Image pour le /start
PHOTO_CARTE = "carte.jpg"   # Image pour le menu
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
# SERVEUR WEB POUR RENDER (Port 10000)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot actif")
    def log_message(self, format, *args):
        pass

def lancer_serveur_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# ==========================================
# INTERFACE CLAVIER
# ==========================================
def menu_principal():
    keyboard = [
        [InlineKeyboardButton("📋 Consulter le menu", callback_data="menu")],
        [InlineKeyboardButton("🕒 Horaires", callback_data="horaires"),
         InlineKeyboardButton("📍 Zone de livraison", callback_data="localisation")],
        [InlineKeyboardButton("⭐ Avis clients", callback_data="avis")]
    ]
    return InlineKeyboardMarkup(keyboard)

def bouton_retour():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour au menu", callback_data="retour")]])

# ==========================================
# LOGIQUE DU BOT
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = f"*{NOM}*\n\n{MESSAGE_ACCUEIL}"
    
    if os.path.exists(PHOTO_ACCUEIL):
        with open(PHOTO_ACCUEIL, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=texte,
                parse_mode="Markdown",
                reply_markup=menu_principal()
            )
    else:
        # Fallback si la photo est manquante pour éviter le crash
        await update.message.reply_text(
            text=f"⚠️ Image {PHOTO_ACCUEIL} manquante\n\n{texte}",
            parse_mode="Markdown",
            reply_markup=menu_principal()
        )

async def gerer_boutons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choix = query.data

    if choix == "menu":
        if os.path.exists(PHOTO_CARTE):
            with open(PHOTO_CARTE, "rb") as photo:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=photo, caption=SERVICES, parse_mode="Markdown"),
                    reply_markup=bouton_retour()
                )
        else:
            await modifier_message(query, f"⚠️ Image {PHOTO_CARTE} manquante\n\n{SERVICES}", bouton_retour())

    elif choix == "horaires":
        await modifier_message(query, HORAIRES, bouton_retour())

    elif choix == "localisation":
        texte_loc = f"📍 *ZONE DE LIVRAISON*\n\nNous livrons sur : {LOCALISATION}"
        await modifier_message(query, texte_loc, bouton_retour())

    elif choix == "avis":
        moyenne = sum(avis_clients) / len(avis_clients)
        texte_avis = (f"⭐ *AVIS CLIENTS*\n\nNote : *{moyenne:.1f} / 5*\n\nLaissez une note :")
        keyboard = [
            [InlineKeyboardButton(f"⭐ {i}", callback_data=f"note_{i}") for i in range(1, 6)],
            [InlineKeyboardButton("⬅️ Retour", callback_data="retour")]
        ]
        await modifier_message(query, texte_avis, InlineKeyboardMarkup(keyboard))

    elif choix.startswith("note_"):
        note = int(choix.split("_")[1])
        avis_clients.append(note)
        await modifier_message(query, f"✅ Merci pour votre note de *{note}/5* !", bouton_retour())

    elif choix == "retour":
        texte = f"*{NOM}*\n\n{MESSAGE_ACCUEIL}"
        if os.path.exists(PHOTO_ACCUEIL):
            with open(PHOTO_ACCUEIL, "rb") as photo:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=photo, caption=texte, parse_mode="Markdown"),
                    reply_markup=menu_principal()
                )
        else:
            await modifier_message(query, texte, menu_principal())

async def modifier_message(query, texte, clavier):
    # Gère la modification selon si le message actuel contient une photo ou non
    if query.message.photo:
        await query.edit_message_caption(caption=texte, parse_mode="Markdown", reply_markup=clavier)
    else:
        await query.edit_message_text(text=texte, parse_mode="Markdown", reply_markup=clavier)

def main():
    if not TOKEN:
        print("ERREUR : TELEGRAM_TOKEN introuvable.")
        return

    threading.Thread(target=lancer_serveur_web, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gerer_boutons))

    print("Bot en ligne...")
    app.run_polling()

if __name__ == "__main__":
    main()
