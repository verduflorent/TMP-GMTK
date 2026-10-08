# TMP-GMTK — Déploiement Render gratuit

Django utilise un Web Service Python et une base PostgreSQL externe persistante (par exemple Neon Free). MongoDB Atlas n'est pas compatible avec les modèles Django actuels.

## Étapes
1. Créer une base PostgreSQL gratuite en région européenne et relever son URL SSL.
2. Préserver les services EzRP existants jusqu'à validation de Django.
3. Le service actuel est de type Node.js : vérifier si Render permet de changer son runtime. Sinon créer un Web Service Python Free distinct pour les essais. Ne pas supprimer l'ancien service avant validation.
4. Configurer le dépôt verduflorent/TMP-GMTK, branche pr2/rules-engine, Root Directory vide, Build Command `bash build-render.sh`, Start Command `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2`.
5. Vérifier que Python 3.14.3 (fichier .python-version) est disponible sur Render.

## Variables secrètes à renseigner dans Render
- DJANGO_DEBUG=0
- DJANGO_SECRET_KEY : secret aléatoire long
- DJANGO_ALLOWED_HOSTS : domaine Render sans protocole
- DJANGO_CSRF_TRUSTED_ORIGINS : URL https:// complète
- DATABASE_URL : chaîne PostgreSQL avec sslmode=require

Ne jamais pousser les secrets dans Git. Ne pas reprendre MONGO_URI ni JWT_SECRET de l'ancien service.

Le script de build installe les dépendances, vérifie Django, collecte les statiques, applique les migrations et synchronise le catalogue Monster. Prévoir la création d'un superutilisateur séparément.

Les offres gratuites peuvent avoir des limites d'activité et de stockage. Une URL onrender.com existante n'est pas garantie transférable vers un autre service.
