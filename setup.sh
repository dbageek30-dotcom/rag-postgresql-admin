#!/bin/bash
set -e

echo "=== Installation du pipeline RAG PostgreSQL ==="

# ------------------------------------------------------------------------------
# 1. Installation des dépendances Python
# ------------------------------------------------------------------------------
echo ">>> Installation des dépendances Python"
pip3 install torch==2.2.2+cpu --index-url https://download.pytorch.org/whl/cpu

pip3 install -r requirements.txt --no-cache-dir

# ------------------------------------------------------------------------------
# 2. Installation PostgreSQL + pgvector
# ------------------------------------------------------------------------------
echo ">>> Installation PostgreSQL + pgvector"

if [ ! -f /usr/share/keyrings/postgresql.gpg ]; then
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        | sudo gpg --dearmor -o /usr/share/keyrings/postgresql.gpg
fi

echo "deb [signed-by=/usr/share/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
    | sudo tee /etc/apt/sources.list.d/pgdg.list > /dev/null

sudo apt update
sudo apt install -y postgresql-18 postgresql-18-pgvector postgresql-contrib-18

# ------------------------------------------------------------------------------
# 3. Vérification PostgreSQL
# ------------------------------------------------------------------------------
echo ">>> Vérification de PostgreSQL"
if ! sudo -u postgres psql -c "SELECT 1;" >/dev/null 2>&1; then
    echo "⚠ PostgreSQL ne semble pas démarré."
    exit 1
fi

# ------------------------------------------------------------------------------
# 4. Demande des informations utilisateur
# ------------------------------------------------------------------------------
read -p "Nom de l'utilisateur PostgreSQL (ex: rag_user) : " RAG_USER
read -s -p "Mot de passe pour ${RAG_USER} : " RAG_PASSWORD
echo ""

# ------------------------------------------------------------------------------
# 5. Création base rag
# ------------------------------------------------------------------------------
echo ">>> Création de la base rag si nécessaire"
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='rag'" | grep -q 1; then
    sudo -u postgres psql -c "CREATE DATABASE rag"
fi

# ------------------------------------------------------------------------------
# 6. Création utilisateur
# ------------------------------------------------------------------------------
echo ">>> Création de l'utilisateur ${RAG_USER}"
sudo -u postgres psql <<EOF
DO \$\$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${RAG_USER}') THEN
        EXECUTE format('DROP ROLE %I', '${RAG_USER}');
    END IF;
END
\$\$;
EOF

sudo -u postgres psql -c "CREATE USER ${RAG_USER} WITH PASSWORD '${RAG_PASSWORD}'"

# ------------------------------------------------------------------------------
# 7. Création table documents
# ------------------------------------------------------------------------------
echo ">>> Création de la table documents"
sudo -u postgres psql -d rag <<EOF
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

DROP TABLE IF EXISTS documents;

CREATE TABLE documents (
    id        SERIAL PRIMARY KEY,
    content   TEXT NOT NULL,
    metadata  JSONB NOT NULL,
    embedding vector(768),
    source    TEXT NOT NULL DEFAULT 'unknown',
    version   TEXT NOT NULL DEFAULT 'unknown'
);

CREATE INDEX IF NOT EXISTS documents_embedding_hnsw_idx
    ON documents USING hnsw (embedding vector_l2_ops);

GRANT CONNECT ON DATABASE rag TO ${RAG_USER};
GRANT USAGE ON SCHEMA public TO ${RAG_USER};
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE documents TO ${RAG_USER};
GRANT USAGE, SELECT ON SEQUENCE documents_id_seq TO ${RAG_USER};
EOF

# ------------------------------------------------------------------------------
# 8. Choix du mode LLM
# ------------------------------------------------------------------------------
echo "Choisir le mode LLM :
1) RAG only (pas de LLM)
2) LLM local distant (Ollama sur une autre machine)
3) LLM distant via API (OpenAI, Groq, DeepSeek, etc.)
"
read -p "Votre choix [1/2/3] : " LLM_CHOICE

LLM_MODE="none"
LLM_PROVIDER=""
LLM_MODEL=""
LLM_API_KEY=""
LLM_URL=""

case "$LLM_CHOICE" in
    2)
        LLM_MODE="local"
        read -p "Adresse du serveur Ollama (ex: http://192.168.1.50:11434/api/chat) : " LLM_URL
        read -p "Nom du modèle (ex: qwen2.5:7b) : " LLM_MODEL
        ;;
    3)
        LLM_MODE="remote"
        read -p "Fournisseur (openai, groq, deepseek, mistral) : " LLM_PROVIDER
        read -p "Nom du modèle (ex: gpt-4.1) : " LLM_MODEL
        read -p "Clé API : " LLM_API_KEY
        ;;
esac

# ------------------------------------------------------------------------------
# 9. Génération du fichier .env
# ------------------------------------------------------------------------------
echo ">>> Génération du fichier .env"

cat > .env <<EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag
DB_USER=${RAG_USER}
DB_PASSWORD=${RAG_PASSWORD}

EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
RERANK_MODEL=BAAI/bge-reranker-large

LLM_MODE=${LLM_MODE}
LLM_PROVIDER=${LLM_PROVIDER}
LLM_MODEL=${LLM_MODEL}
LLM_API_KEY=${LLM_API_KEY}
LLM_URL=${LLM_URL}
EOF

# ------------------------------------------------------------------------------
# 10. Ingestion + embeddings
# ------------------------------------------------------------------------------
echo ">>> Installation des dépendances ingestion"
pip3 install -r requirements-ingest.txt

echo ">>> Ingestion de la documentation"
python3 script_python/parse_all.py

echo ">>> Génération des embeddings"
python3 script_python/generate_embeddings.py

echo "=== Installation terminée ==="

