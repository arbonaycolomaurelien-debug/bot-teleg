import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ==========================================
# VOS RÉGLAGES PERSONNALISÉS
# ==========================================
NOM = "Amiens Livraison"
PHOTO_ACCUEIL = "menu.jpg"   # Photo affichée au démarrage (/start)
PHOTO_CARTE = "carte.jpg"    # Photo affichée quand on clique sur "Consulter le menu"
LOCALISATION = "Amiens et alentours"

MESSAGE_ACCUEIL = "Bonjour ! Nous sommes disponibles sur Amiens, n'hésitez pas à consulter le menu ci-dessous :"

HORAIRES = """🕒 NOS HORAIRES
Disponible tous les jours de 10h00 à 01h00 du matin."""

SERVICES = """📋 NOTRE MENU & SERVICES
• Livraison rapide sur Amiens et alentours
• Produits sélectionnés avec soin
• Service discret et réactif"""

# Liste de départ des avis clients (max 5 étoiles)
avis_clients = [5]

# ==========================================
# FONCTIONNEMENT DU BOT
# ==========================================
def menu_principal():
    clavier = [
        [InlineKeyboardButton("📋 Consulter le menu", callback_data="services")],
        [InlineKeyboardButton("🕒 Horaires (10h - 1h00)", callback_data="horaires")],
        [InlineKeyboardButton("📍 Localisation (Amiens)", callback_data="localisation")],
        [InlineKeyboardButton("⭐ Avis clients", callback_data="avis")]
    ]
    return InlineKeyboardMarkup(clavier)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = f"⚜️ {NOM} ⚜️\n\n{MESSAGE_ACCUEIL}"
    if os.path.exists(PHOTO_ACCUEIL):
        with open(PHOTO_ACCUEIL, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=texte, reply_markup=menu_principal())
    else:
        await update.message.reply_text(texte, reply_markup=menu_principal())

async def boutons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    clavier_retour = [[InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu")]]
    markup_retour = InlineKeyboardMarkup(clavier_retour)

    async def repondre(nouveau_texte, clavier_bouton):
        if query.message.photo:
            await query.edit_message_caption(caption=nouveau_texte, reply_markup=clavier_bouton)
        else:
            await query.edit_message_text(text=nouveau_texte, reply_markup=clavier_bouton)

    if query.data == "services":
        if os.path.exists(PHOTO_CARTE):
            with open(PHOTO_CARTE, "rb") as photo:
                if query.message.photo:
                    await query.edit_message_media(
                        media=InputMediaPhoto(media=photo, caption=SERVICES),
                        reply_markup=markup_retour
                    )
                else:
                    await query.message.reply_photo(photo=photo, caption=SERVICES, reply_markup=markup_retour)
        else:
            await repondre(SERVICES, markup_retour)

    elif query.data == "horaires":
        await repondre(HORAIRES, markup_retour)

    elif query.data == "localisation":
        await repondre(f"📍 ZONE DE LIVRAISON\nNous intervenons sur : {LOCALISATION}.", markup_retour)

    elif query.data == "avis":
        moyenne = round(sum(avis_clients) / len(avis_clients), 1)
        nb_avis = len(avis_clients)
        clavier_avis = [
            [
                InlineKeyboardButton("⭐ 1", callback_data="note_1"),
                InlineKeyboardButton("⭐ 2", callback_data="note_2"),
                InlineKeyboardButton("⭐ 3", callback_data="note_3"),
                InlineKeyboardButton("⭐ 4", callback_data="note_4"),
                InlineKeyboardButton("⭐ 5", callback_data="note_5")],
            [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu")]
        ]
        texte_avis = f"⭐ AVIS CLIENTS ⭐\n\nNote moyenne : {moyenne}/5 ({nb_avis} avis)\n\nCliquez sur une note ci-dessous pour laisser votre avis (max 5 étoiles) :"
        await repondre(texte_avis, InlineKeyboardMarkup(clavier_avis))

    elif query.data.startswith("note_"):
        note = int(query.data.split("_")[1])
        if 1 <= note <= 5:
            avis_clients.append(note)
        moyenne = round(sum(avis_clients) / len(avis_clients), 1)
        etoiles = "⭐" * note
        await repondre(
            f"✅ Merci pour votre avis : {etoiles} ({note}/5) !\n\nNouvelle note moyenne : {moyenne}/5 ({len(avis_clients)} avis).",
            markup_retour
        )

    elif query.data == "menu":
        texte = f"⚜️ {NOM} ⚜️\n\n{MESSAGE_ACCUEIL}"
        if os.path.exists(PHOTO_ACCUEIL) and query.message.photo:
            with open(PHOTO_ACCUEIL, "rb") as photo:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=photo, caption=texte),
                    reply_markup=menu_principal()
                )
        else:
            await repondre(texte, menu_principal())


if__ name__ == "main__":
    if not TOKEN:
        print("ERREUR : Fichier .env introuvable ou vide !")
    else:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(boutons))
        print("BOT TELEGRAM DEMARRE !")
        app.run_polling()
