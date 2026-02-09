import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()


# Variables d'environnement pour la base locale (RAG)
DB_NAME = os.getenv("DB_NAME", "rag")
DB_USER = os.getenv("DB_USER", "rag_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))

# Variables d'environnement pour la base distante (workers/tests)
REMOTE_DB_NAME = os.getenv("REMOTE_DB_NAME")
REMOTE_DB_USER = os.getenv("REMOTE_DB_USER")
REMOTE_DB_PASSWORD = os.getenv("REMOTE_DB_PASSWORD")
REMOTE_DB_HOST = os.getenv("REMOTE_DB_HOST")
REMOTE_DB_PORT = os.getenv("REMOTE_DB_PORT")

# Connexion PostgreSQL locale (RAG)
def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Connexion PostgreSQL distante (workers/tests)
def get_remote_connection():
    if not all([REMOTE_DB_NAME, REMOTE_DB_USER, REMOTE_DB_PASSWORD, REMOTE_DB_HOST, REMOTE_DB_PORT]):
        raise ValueError("REMOTE_DB_* variables are not fully defined in .env")

    return psycopg2.connect(
        dbname=REMOTE_DB_NAME,
        user=REMOTE_DB_USER,
        password=REMOTE_DB_PASSWORD,
        host=REMOTE_DB_HOST,
        port=int(REMOTE_DB_PORT)
    )

# Connexion globale utilisée par rag.py (NE PAS TOUCHER)
conn = get_connection()

# Charger dynamiquement les sources et versions (NE PAS TOUCHER)
def load_sources_and_versions():
    cur = conn.cursor()
    cur.execute("""
        SELECT source, version
        FROM documents
        GROUP BY source, version
        ORDER BY source;
    """)
    rows = cur.fetchall()
    cur.close()

    mapping = {}
    for source, version in rows:
        mapping[source] = version

    return mapping

# Mapping global accessible dans main.py (NE PAS TOUCHER)
SOURCE_VERSION_MAP = load_sources_and_versions()

