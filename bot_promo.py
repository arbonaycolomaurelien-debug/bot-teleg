def main():
    if not TOKEN:
        print("ERREUR : TELEGRAM_TOKEN est vide.")
        return

    # Lancement du serveur de santé pour Render
    threading.Thread(target=lancer_serveur_web, daemon=True).start()

    # Configuration du bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gerer_boutons))

    print("Bot en cours de démarrage...")
    
    # drop_pending_updates=True permet d'ignorer les messages envoyés 
    # pendant que le bot était éteint pour éviter qu'il ne sature
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
