f"⭐ *AVIS CLIENTS*\n\n"
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
    if query.message.photo:
        await query.edit_message_caption(caption=texte, parse_mode="Markdown", reply_markup=clavier)
    else:
        await query.edit_message_text(text=texte, parse_mode="Markdown", reply_markup=clavier)

def main():
    if not TOKEN:
        raise ValueError("La variable d'environnement TELEGRAM_TOKEN est manquante !")

    threading.Thread(target=lancer_serveur_web, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gerer_boutons))

    print("Bot démarré...")
    app.run_polling()

if name == "main":
    main()
