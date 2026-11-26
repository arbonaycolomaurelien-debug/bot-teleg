# Amiens Livraison — déploiement Render

## Fichiers
- `bot.py` : version adaptée à Render avec webhook Telegram.
- `requirements.txt` : dépendances.
- `menu.jpg` et `carte.jpg` : ajoutez vos images si vous souhaitez les afficher.

## Réglages Render
Créez un **Web Service** relié au dépôt GitHub contenant ces fichiers.

- Runtime : Python
- Build Command : `pip install -r requirements.txt`
- Start Command : `python bot.py`
- Instance Type : Free (si disponible)

Dans **Environment**, ajoutez :
- `TELEGRAM_TOKEN` : le token de votre bot (à garder secret)
- `WEBHOOK_URL` : l'URL HTTPS Render du service, par exemple `https://nom-du-service.onrender.com`
- `WEBHOOK_SECRET` : une chaîne secrète aléatoire d'au moins 16 caractères, composée de lettres, chiffres, `_` ou `-`.

Render fournit automatiquement la variable `PORT`.

## Important
- Ne mettez jamais le token dans GitHub.
- Ajoutez `menu.jpg` et `carte.jpg` à la racine du dépôt si vous voulez les photos.
- L'offre gratuite Render peut mettre le service en veille après 15 minutes sans trafic entrant. Le premier réveil peut prendre environ une minute.
- Les avis sont stockés en mémoire et sont réinitialisés lors d'un redémarrage/déploiement.
