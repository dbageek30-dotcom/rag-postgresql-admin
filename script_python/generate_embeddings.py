import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ---------------------------------------------------------------------
# 1. Charger la configuration depuis .env
# ---------------------------------------------------------------------

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "rag")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")

# ---------------------------------------------------------------------
# 2. Charger le modèle d'embedding
# ---------------------------------------------------------------------

print(f"Chargement du modèle d'embedding : {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)

# ---------------------------------------------------------------------
# 3. Connexion PostgreSQL
# ---------------------------------------------------------------------

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# ---------------------------------------------------------------------
# 4. Récupérer les documents sans embedding
# ---------------------------------------------------------------------

cur.execute("""
    SELECT id, content
    FROM documents
    WHERE embedding IS NULL
    ORDER BY id ASC;
""")
rows = cur.fetchall()

print(f"Documents à traiter : {len(rows)}")

# ---------------------------------------------------------------------
# 5. Générer les embeddings en batch
# ---------------------------------------------------------------------

BATCH_SIZE = 32

for i in tqdm(range(0, len(rows), BATCH_SIZE), desc="Génération embeddings"):
    batch = rows[i:i+BATCH_SIZE]
    ids = [row[0] for row in batch]
    texts = [row[1] for row in batch]

    embeddings = model.encode(texts).tolist()

    for doc_id, emb in zip(ids, embeddings):
        cur.execute("""
            UPDATE documents
            SET embedding = %s
            WHERE id = %s;
        """, (emb, doc_id))

    conn.commit()

cur.close()
conn.close()

print("Embeddings générés et insérés avec succès.")

