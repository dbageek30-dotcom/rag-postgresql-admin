import psycopg2
from sentence_transformers import SentenceTransformer

# 1. Charger le modèle d'embedding
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# 2. Connexion PostgreSQL
conn = psycopg2.connect(
    dbname="rag",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# 3. Récupérer les documents sans embedding
cur.execute("""
    SELECT id, content
    FROM documents
    WHERE embedding IS NULL;
""")
rows = cur.fetchall()

print(f"Documents à traiter : {len(rows)}")

# 4. Générer et insérer les embeddings
for doc_id, content in rows:
    embedding = model.encode(content).tolist()  # convertir en liste Python

    cur.execute("""
        UPDATE documents
        SET embedding = %s
        WHERE id = %s;
    """, (embedding, doc_id))

conn.commit()
cur.close()
conn.close()

print("Embeddings générés et insérés.")

