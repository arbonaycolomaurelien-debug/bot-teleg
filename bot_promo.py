import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ==========================================
# RÉGLAGES
# ==========================================
NOM = "Livraison à Amiens"
PHOTO_ACCUEIL = "https://i.postimg.cc/sX97S6S8/menu.jpg" 

# Votre lien Signal pour la discrétion
LIEN_SIGNAL = "https://signal.me/#eu/XA8YULEl38zYvnvfostSl1lD9OSL5YYMIm1SvLOg-i8mRnf1yXZH-YpYtgH-za3h"

LOCALISATION = "Amiens et environs"
MESSAGE_ACCUEIL = "Bonjour ! Nous sommes disponibles sur Amiens, n'hésitez pas à consulter le menu ci-dessous !"

HORAIRES = "🕒 *NOS HORAIRES*\nDisponible tous les jours de 10h00 à 01h00 du matin."
SERVICES = "📋 *NOTRE MENU & SERVICES*\n• Livraison rapide sur Amiens\n• Produits sélectionnés avec soin\n• Service discret et réactif"

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
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

# ==========================================
# BOUTONS
# ==========================================
def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Consulter le menu", callback_data="menu")],
        [InlineKeyboardButton("🔒 Commande sur Signal (Discrétion)", url=LIEN_SIGNAL)],
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
        photo=PHOTO_ACCUEIL,
        caption=f"*{NOM}*\n\n{MESSAGE_ACCUEIL}",
        parse_mode="Markdown",
        reply_markup=menu_principal()
    )

async def gerer_boutons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choix = query.data

    # Sections gardant la photo
    if choix == "menu":
        await query.edit_message_caption(caption=SERVICES, parse_mode="Markdown", reply_markup=bouton_retour())
    
    elif choix == "retour":
        if not query.message.photo:
            await query.message.delete()
            await query.message.reply_photo(
                photo=PHOTO_ACCUEIL,
                caption=f"*{NOM}*\n\n{MESSAGE_ACCUEIL}",
                parse_mode="Markdown",
                reply_markup=menu_principal()
            )
        else:
            await query.edit_message_caption(
                caption=f"*{NOM}*\n\n{MESSAGE_ACCUEIL}",
                parse_mode="Markdown",
                reply_markup=menu_principal()
            )

    # Sections en texte pur (sans photo pour plus de clarté)
    else:
        texte = ""
        clavier = bouton_retour()

        if choix == "horaires":
            texte = HORAIRES
        elif choix == "localisation":
            texte = f"📍 *ZONE DE LIVRAISON*\n\nNous livrons sur : {LOCALISATION}"
        elif choix == "avis":
            moyenne = sum(avis_clients) / len(avis_clients)
            texte = f"⭐ *AVIS CLIENTS*\n\nNote : *{moyenne:.1f} / 5*\n\nLaissez une note :"
            clavier = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"⭐ {i}", callback_data=f"note_{i}") for i in range(1, 6)],
                [InlineKeyboardButton("⬅️ Retour", callback_data="retour")]
            ])
        elif choix.startswith("note_"):
            avis_clients.append(int(choix.split("_")[1]))
            texte = "✅ Merci pour votre note !"

        if query.message.photo:
            await query.message.delete()
            await query.message.reply_text(text=texte, parse_mode="Markdown", reply_markup=clavier)
        else:
            await query.edit_message_text(text=texte, parse_mode="Markdown", reply_markup=clavier)

def main():
    if not TOKEN:
        print("Variable TELEGRAM_TOKEN manquante.")
        return
    
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gerer_boutons))
    
    print("Bot en ligne avec lien Signal...")
    app.run_polling()

if __name__ == "__main__":
    main()
