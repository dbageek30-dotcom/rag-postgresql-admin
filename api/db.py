import psycopg2
import os

# Variables d'environnement
DB_NAME = os.getenv("DB_NAME", "rag")
DB_USER = os.getenv("DB_USER", "rag_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))

# Connexion PostgreSQL
def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Connexion globale utilisée par rag.py
conn = get_connection()

# Charger dynamiquement les sources et versions
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

# Mapping global accessible dans main.py
SOURCE_VERSION_MAP = load_sources_and_versions()

