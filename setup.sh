#!/bin/bash

echo "=== Installation du pipeline RAG PostgreSQL ==="

# 1. Installation des dépendances Python
echo ">>> Installation des dépendances Python"
pip install -r requirements.txt

# 2. Création de la table PostgreSQL
echo ">>> Création de la table documents dans PostgreSQL"
psql postgres <<EOF
CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS documents;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(768),
    metadata JSONB
);
EOF

# 3. Création des index vectoriels
echo ">>> Création des index vectoriels (HNSW)"
psql postgres <<EOF
CREATE INDEX IF NOT EXISTS idx_documents_embedding_hnsw
ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
EOF

# 4. Ingestion de la documentation
echo ">>> Ingestion de la documentation PostgreSQL"
python3 script_python/parse_all_docs.py

echo "=== Installation terminée ==="
echo "Ton pipeline RAG est prêt à l'emploi."
