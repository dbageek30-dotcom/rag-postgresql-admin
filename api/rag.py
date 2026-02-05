from sentence_transformers import SentenceTransformer
from .db import get_connection

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

def rag_query(question, top_k=5):
    emb = model.encode(question).tolist()

    # Convertit en format pgvector
    vec = "[" + ",".join(str(x) for x in emb) + "]"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT content, metadata, embedding <=> %s::vector AS distance
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (vec, vec, top_k))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "content": r[0],
            "metadata": r[1],
            "distance": float(r[2])
        }
        for r in rows
    ]

