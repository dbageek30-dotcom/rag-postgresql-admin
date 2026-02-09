#!/bin/bash

cd /var/lib/postgresql/rag-postgresql-admin

# Ajouter tous les fichiers modifiés et nouveaux
git add -A

# Commit avec timestamp
git commit -m "Auto-save $(date '+%Y-%m-%d %H:%M:%S')" >/dev/null 2>&1

# Push silencieux
git push origin main >/dev/null 2>&1

