#!/bin/bash

echo "=== Installation du pipeline RAG PostgreSQL ==="

# 1. Installation des dépendances Python
echo ">>> Installation des dépendances Python"
pip3 install -r requirements.txt

# 2. Ajouter le dépôt PostgreSQL officiel (nécessaire pour pgvector)
echo ">>> Ajout du dépôt PostgreSQL officiel"
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

sudo apt update

# 3. Installer pgvector pour PostgreSQL 18
echo ">>> Installation de pgvector"
sudo apt install -y postgresql-18-pgvector

# 4. Vérifier que PostgreSQL tourne
echo ">>> Vérification du service PostgreSQL"
if ! systemctl is-active --quiet postgresql; then
    echo "PostgreSQL n'est pas démarré, démarrage..."
    sudo systemctl start postgresql
fi

# 5. Création de la base RAG
echo ">>> Création de la base rag"
sudo -u postgres psql <<EOF
CREATE DATABASE rag;
EOF

# 6. Création des tables et index
echo ">>> Création des tables et index"
sudo -u postgres psql -d rag <<EOF
CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS documents;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(768)
);

CREATE INDEX IF NOT EXISTS idx_documents_embedding
ON documents
USING hnsw (embedding vector_cosine_ops);
EOF

# 7. Ingestion de la documentation
echo ">>> Ingestion de la documentation PostgreSQL"
python3 script_python/parse_all.py

echo "=== Installation terminée ==="
echo "Ton pipeline RAG est prêt à l'emploi."

