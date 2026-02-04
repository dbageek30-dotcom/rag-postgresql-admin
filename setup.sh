#!/bin/bash

echo "=== Installation du pipeline RAG PostgreSQL ==="

# 1. Installation des dépendances Python
echo ">>> Installation des dépendances Python"
pip3 install -r requirements.txt

# 2. Ajout du dépôt PostgreSQL officiel (si besoin) + installation pgvector
echo ">>> Ajout du dépôt PostgreSQL officiel et installation de pgvector"
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-18-pgvector

# 3. Vérifier que PostgreSQL tourne
echo ">>> Vérification du service PostgreSQL"
if ! systemctl is-active --quiet postgresql; then
    echo "PostgreSQL n'est pas démarré, démarrage..."
    sudo systemctl start postgresql
fi

# 4. Demander les infos pour l'utilisateur applicatif
echo ">>> Création d'un utilisateur PostgreSQL dédié pour le RAG"
read -p "Nom de l'utilisateur PostgreSQL à créer (par ex. rag_user) : " RAG_USER
read -s -p "Mot de passe pour l'utilisateur ${RAG_USER} : " RAG_PASSWORD
echo ""

# 5. Création de la base et de l'utilisateur
echo ">>> Création de la base 'rag' et de l'utilisateur '${RAG_USER}'"
sudo -u postgres psql <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rag') THEN
      PERFORM dblink_exec('dbname=' || current_database(), 'CREATE DATABASE rag');
   END IF;
END
\$do\$;

DO
\$do\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${RAG_USER}') THEN
      PERFORM dblink_exec('dbname=' || current_database(), 'CREATE USER ${RAG_USER} WITH PASSWORD ''${RAG_PASSWORD}''');
   END IF;
END
\$do\$;
EOF

# 6. Création des extensions, table et index dans la base rag
echo ">>> Création de la table documents et des index dans la base rag"
sudo -u postgres psql -d rag <<EOF
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Table documents
DROP TABLE IF EXISTS documents;

CREATE TABLE documents (
    id        SERIAL       PRIMARY KEY,
    content   TEXT         NOT NULL,
    metadata  JSONB        NOT NULL,
    embedding vector(768)
);

-- Index sur les métadonnées
CREATE INDEX IF NOT EXISTS documents_chapter_idx
    ON documents ((metadata ->> 'chapter'));

CREATE INDEX IF NOT EXISTS documents_section_idx
    ON documents ((metadata ->> 'section'));

CREATE INDEX IF NOT EXISTS documents_version_idx
    ON documents ((metadata ->> 'version'));

CREATE INDEX IF NOT EXISTS documents_tags_idx
    ON documents USING GIN ((metadata -> 'tags'));

-- Index HNSW sur l'embedding
CREATE INDEX IF NOT EXISTS documents_embedding_hnsw_idx
    ON documents
    USING hnsw (embedding vector_l2_ops);

-- Droits pour l'utilisateur applicatif
GRANT CONNECT ON DATABASE rag TO ${RAG_USER};
GRANT USAGE ON SCHEMA public TO ${RAG_USER};
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE documents TO ${RAG_USER};
GRANT USAGE, SELECT ON SEQUENCE documents_id_seq TO ${RAG_USER};
EOF

# 7. Ingestion de la documentation
echo ">>> Ingestion de la documentation PostgreSQL"
python3 script_python/parse_all.py

echo "=== Installation terminée ==="
echo "Ton pipeline RAG est prêt à l'emploi."

