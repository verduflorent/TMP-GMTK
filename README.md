# TMP-GMTK

Game Master Toolkit pour **THE MOIRA PROTOCOL**.

La documentation autoritaire du projet se trouve dans `docs/` et les règles de travail prioritaires dans `AGENTS.md`.

## Développement local

Prérequis : Python 3.14 et Poetry 2.4+.

```powershell
poetry install
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

Puis ouvrir `http://127.0.0.1:8000/`.

## Vérifications

```powershell
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run python manage.py test
```

## PR 1

Le premier jalon installe uniquement le socle Django, l'authentification privée, les relations de données du domaine, une Table d'accueil vide et les tests d'intégrité. Le moteur de règles TMP, le référentiel natif complet, l'éditeur, le randomizer et le Dice Roller restent hors périmètre de cette PR.
