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
PHOTO_ACCUEIL = "menu.jpg"  # Photo affichée au démarrage (/start)
PHOTO_CARTE = "carte.jpg"   # Photo affichée quand on clique sur "Consulter le menu"
LOCALISATION = "Amiens et environs"

MESSAGE_ACCUEIL = "Bonjour ! Nous sommes disponibles sur Amiens, n'hésitez pas à consulter le menu ci-dessous !"

HORAIRES = """🕒 *NOS HORAIRES*
Disponible tous les jours de 10h00 à 01h00 du matin."""

SERVICES = """📋 *NOTRE MENU & SERVICES*
• Livraison rapide sur Amiens et alentours
• Produits sélectionnés avec soin
• Service discret et réactif"""

# Liste de départ des avis clients
avis_clients = [5]

# ==========================================
# SERVEUR WEB POUR RENDER
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
# FONCTIONNEMENT DU BOT
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
    keyboard = [[InlineKeyboardButton("⬅️ Retour au menu principal", callback_data="retour")]]
    return InlineKeyboardMarkup(keyboard)

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
        await update.message.reply_text(
            text=texte,
            parse_mode="Markdown",
            reply_markup=menu_principal()
        )

async def gerer_boutons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choix = query.data

    if choix == "menu":
        if os.path.exists(PHOTO_CARTE) and query.message.photo:
            with open(PHOTO_CARTE, "rb") as photo:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=photo, caption=SERVICES, parse_mode="Markdown"),
                    reply_markup=bouton_retour()
                )
        else:
            await modifier_message(query, SERVICES, bouton_retour())

    elif choix == "horaires":
        await modifier_message(query, HORAIRES, bouton_retour())

    elif choix == "localisation":
        texte_loc = f"📍 *ZONE DE LIVRAISON*\n\nNous livrons sur : {LOCALISATION}"
        await modifier_message(query, texte_loc, bouton_retour())

    elif choix == "avis":
        moyenne = sum(avis_clients) / len(avis_clients)
        texte_avis = (f"⭐ *AVIS CLIENTS*\n\n"
            f"Note moyenne : *{moyenne:.1f} / 5* ({len(avis_clients)} avis)\n\n"
            f"Cliquez ci-dessous pour laisser une note :"
        )
        keyboard = [
            [
                InlineKeyboardButton("⭐ 1", callback_data="note_1"),
                InlineKeyboardButton("⭐ 2", callback_data="note_2"),
                InlineKeyboardButton("⭐ 3", callback_data="note_3"),
                InlineKeyboardButton("⭐ 4", callback_data="note_4"),
                InlineKeyboardButton("⭐ 5", callback_data="note_5"),
            ],
            [InlineKeyboardButton("⬅️ Retour au menu principal", callback_data="retour")]
        ]
        await modifier_message(query, texte_avis, InlineKeyboardMarkup(keyboard))

    elif choix.startswith("note_"):
        note = int(choix.split("_")[1])
        avis_clients.append(note)
        texte_merci = f"✅ Merci pour votre note de *{note}/5* !"
        await modifier_message(query, texte_merci, bouton_retour())

    elif choix == "retour":
        texte = f"*{NOM}*\n\n{MESSAGE_ACCUEIL}"
        if os.path.exists(PHOTO_ACCUEIL) and query.message.photo:
            with open(PHOTO_ACCUEIL, "rb") as photo:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=photo, caption=texte, parse_mode="Markdown"),
                    reply_markup=menu_principal()
                )
        else:
            await modifier_message(query, texte, menu_principal())

async def modifier_message(query, texte, clavier):
    # Cette fonction gère la modification du texte, qu'il y ait une photo ou non
    if query.message.photo:
        await query.edit_message_caption(caption=texte, parse_mode="Markdown", reply_markup=clavier)
    else:
        await query.edit_message_text(text=texte, parse_mode="Markdown", reply_markup=clavier)

def main():
    if not TOKEN:
        print("Erreur: La variable TELEGRAM_TOKEN est vide ou absente.")
        return

    # Lancement du serveur de santé pour Render
    threading.Thread(target=lancer_serveur_web, daemon=True).start()

    # Configuration du bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gerer_boutons))

    print("Bot démarré avec succès...")
    app.run_polling()

if __name__ == "__main__":
    main()
