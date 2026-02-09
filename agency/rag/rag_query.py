from agency.llm.embedding_singleton import EmbeddingSingleton
from agency.db.connection import conn

# Singleton : un seul modèle d'embedding pour toute l'application
embedder = EmbeddingSingleton.get_model()

def rag_query(query: str, source: str = None, version: str = None):
    embedding = embedder.encode(query).tolist()
    vector_str = "[" + ",".join(str(x) for x in embedding) + "]"

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

    sql = f"""
        SELECT content, metadata, embedding
        FROM documents
        {where_sql}
        ORDER BY embedding <-> %s::vector
        LIMIT 5;
    """

    params.append(vector_str)

    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()

    results = []
    for content, metadata, emb in rows:
        results.append({
            "content": content,
            "metadata": metadata
        })

    return {"query": query, "results": results}

