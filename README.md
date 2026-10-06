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
