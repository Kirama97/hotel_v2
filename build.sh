#!/usr/bin/env bash
# build.sh — exécuté par Render à chaque déploiement

set -o errexit  # Arrête si une commande échoue

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Appliquer les migrations
python manage.py migrate