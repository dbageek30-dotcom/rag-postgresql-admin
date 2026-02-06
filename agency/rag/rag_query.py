from sentence_transformers import SentenceTransformer
from agency.db.connection import conn

# Modèle d'embedding
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

def rag_query(query: str, source: str = None, version: str = None):
    # Génération de l'embedding
    embedding = embedder.encode(query).tolist()

    # Conversion en format pgvector : "[0.12,-0.03,...]"
    vector_str = "[" + ",".join(str(x) for x in embedding) + "]"

    # Construction dynamique du WHERE
    where_clauses = []
    params = []

    if source:
        where_clauses.append("source = %s")
        params.append(source)

    if version:
        where_clauses.append("version = %s")
        params.append(version)

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    # Requête SQL avec cast explicite ::vector
    sql = f"""
        SELECT content, metadata, embedding
        FROM documents
        {where_sql}
        ORDER BY embedding <-> %s::vector
        LIMIT 5;
    """

    # Ajout de l'embedding converti
    params.append(vector_str)

    # Exécution
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()

    # Formatage du résultat
    results = []
    for content, metadata, emb in rows:
        results.append({
            "content": content,
            "metadata": metadata
        })

    return {"query": query, "results": results}
