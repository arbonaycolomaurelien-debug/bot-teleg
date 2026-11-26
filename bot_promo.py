py
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "9275289835:AAHp9OKE_gOmUSTe2yG2Iqjyymtz8WnbWw0"

NOM = "Livraison à Amiens"
PHOTO_URL = "https://i.postimg.cc/nc5RK9w0/dwibalzac80.png"

LOCALISATION = "Amiens et environs"
MESSAGE_ACCUEIL = "Bonjour ! Nous sommes disponibles sur Amiens, n'hésitez pas à consulter le menu ci-dessous !"
HORAIRES = "🕒 *NOS HORAIRES*\nDisponible tous les jours de 10h00 à 01h00 du matin."
SERVICES = "📋 *NOTRE MENU & SERVICES*\n• Livraison rapide sur Amiens\n• Produits sélectionnés\n• Service discret"

avis_clients = [5]

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot actif")
    def log_message(self, format, *args): pass

def lancer_serveur_web():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Consulter le menu", callback_data="menu")],
        [InlineKeyboardButton("🕒 Horaires", callback_data="horaires"),
         InlineKeyboardButton("📍 Zone de livraison", callback_data="localisation")],
        [InlineKeyboardButton("⭐ Avis clients", callback_data="avis")]
    ])

def bouton_retour():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour au menu", callback_data="retour")]])

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

    # CAS OÙ ON GARDE LA PHOTO (Menu)
    if choix == "menu":
        await query.edit_message_caption(caption=SERVICES, parse_mode="Markdown", reply_markup=bouton_retour())
    
    # CAS DE RETOUR À L'ACCUEIL (On remet la photo)
    elif choix == "retour":
        if not query.message.photo:
            await query.message.delete()
            await query.message.reply_photo(
                photo=PHOTO_URL,
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

    # CAS OÙ ON ENLÈVE LA PHOTO (Horaires, Localisation, Avis)
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

        # Si le message actuel a une photo, on le supprime et on envoie un message texte simple
        if query.message.photo:
            await query.message.delete()
            await query.message.reply_text(text=texte, parse_mode="Markdown", reply_markup=clavier)
        else:
            await query.edit_message_text(text=texte, parse_mode="Markdown", reply_markup=clavier)

def main():
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gerer_boutons))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
