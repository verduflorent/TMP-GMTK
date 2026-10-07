# TMP-GMTK

Game Master Toolkit pour **THE MOIRA PROTOCOL**.

Le MVP est recentré sur le **Monster Builder** : générer rapidement des Mobs, corriger leur équipement, préparer une rencontre puis la jouer sur Table numérique ou l'imprimer.

La documentation autoritaire du projet se trouve dans `docs/` et les règles de travail prioritaires dans `AGENTS.md`.

## Développement local

Prérequis : Python 3.14 et Poetry 2.4+.

```powershell
poetry install
poetry run python manage.py migrate
poetry run python manage.py seed_monster_catalogue
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

Puis ouvrir `http://127.0.0.1:8000/`.

Le catalogue Monster n'est pas stocké dans Git sous forme de base SQLite : la commande `seed_monster_catalogue` recrée ou actualise de façon idempotente les armes et implants officiels.

## Vérifications locales

```powershell
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run python manage.py test
```

Le workflow du projet privilégie les tests locaux avant commit/merge. La CI GitHub n'est pas la boucle de test ordinaire.

## État du chantier

PR1 fournit le socle Django et l'authentification privée.

PR2 fournit le domaine Monster Builder, le moteur de scaling/attaque Mob et le référentiel reproductible des armes et implants.

PR3 porte le premier Monster Builder visible : génération de lots, pondérations, attribution d'équipement, édition rapide et Bestiaire.

## Interface TMP

La présentation utilise les deux PNG officiels dans `toolkit/static/img/`, le thème
`toolkit/static/css/tmp-theme.css` et les interactions visuelles `toolkit/static/js/tmp-ui.js`.
Les assets sont dans le répertoire statique de l'application pour être trouvés par
Django sans modifier ses settings. Le déploiement doit servir les fichiers statiques
selon sa procédure habituelle (et collectstatic, s'il l'utilise).

Le front conserve les formulaires, URLs, champs et calculs existants. La vue compacte
est locale à la page. Le D20 affiche le résultat du serveur ; son animation et la
mention Perfect sur un 1 ne modifient aucun résultat ni aucune règle Mob.
Aucun compteur de tour ou statut de session fictif n'est ajouté.
Les polices Anton et Rajdhani utilisent le chargement Google Fonts déjà présent,
avec des polices de repli si le réseau est indisponible.
