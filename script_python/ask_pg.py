#!/usr/bin/env python3
import sys
import json
import textwrap
import psycopg2
import requests
import os

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, CrossEncoder

# =========================
#  Charger la configuration
# =========================
load_dotenv()

# Embeddings + Reranker
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
RERANK_MODEL_NAME = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-large")

# PostgreSQL
PG_CONN_INFO = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "rag"),
    "user": os.getenv("DB_USER", "rag_user"),
    "password": os.getenv("DB_PASSWORD", "")
}

# LLM
LLM_URL = os.getenv("LLM_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

# =========================
#  Charger les modèles
# =========================
print(f"Loading embedding model: {EMBED_MODEL_NAME}")
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

print(f"Loading reranker model: {RERANK_MODEL_NAME}")
reranker = CrossEncoder(RERANK_MODEL_NAME)


# =========================
#  Embedding
# =========================
def get_embedding(text: str):
    return embed_model.encode(text, normalize_embeddings=True).tolist()


# =========================
#  Recherche vectorielle
# =========================
def fetch_candidates(question: str, top_k: int = 30, source: str = None):
    emb = get_embedding(question)

    conn = psycopg2.connect(**PG_CONN_INFO)
    cur = conn.cursor()

    if source:
        query = """
            SELECT
                metadata->>'title'   AS title,
                metadata->>'html_id' AS html_id,
                content,
                embedding <-> %s::vector AS distance
            FROM documents
            WHERE source = %s
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """
        cur.execute(query, (emb, source, emb, top_k))
    else:
        query = """
            SELECT
                metadata->>'title'   AS title,
                metadata->>'html_id' AS html_id,
                content,
                embedding <-> %s::vector AS distance
            FROM documents
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """
        cur.execute(query, (emb, emb, top_k))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# =========================
#  Reranking
# =========================
def rerank_candidates(question: str, rows, final_k: int = 6):
    if not rows:
        return []

    pairs = [(question, content) for (_, _, content, _) in rows]
    scores = reranker.predict(pairs)

    scored = list(zip(scores, rows))
    scored.sort(key=lambda x: x[0], reverse=True)

    return [r for (_, r) in scored[:final_k]]


# =========================
#  Contexte
# =========================
def build_context(reranked_rows):
    parts = []
    for title, html_id, content, distance in reranked_rows:
        snippet = textwrap.shorten(content.replace("\n", " "), width=1200, placeholder=" ...")
        parts.append(f"### {title} ({html_id})\n{snippet}\n")
    return "\n\n".join(parts)


# =========================
#  Appel LLM
# =========================
def call_llm(question: str, context: str) -> str:
    if not LLM_URL or not LLM_MODEL:
        return None  # mode NO LLM automatique

    system_prompt = (
        "You are a PostgreSQL server administration assistant. "
        "Answer ONLY using the documentation context provided. "
        "If the answer is not in the context, say exactly: "
        "\"The documentation does not contain this information.\""
    )

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "Here is the documentation context:\n\n"
                    f"{context}\n\n"
                    f"Question: {question}"
                ),
            },
        ],
        "stream": False,
    }

    try:
        resp = requests.post(LLM_URL, json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[NO LLM] Impossible d'appeler le LLM : {e}")
        return None

    if isinstance(data, dict) and "message" in data:
        return data["message"]["content"]
    elif isinstance(data, dict) and "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        return str(data)


# =========================
#  Fonction API-friendly
# =========================
def ask_pg(question: str, no_llm: bool = False, source: str = None) -> str:
    candidates = fetch_candidates(question, top_k=30, source=source)
    top_rows = rerank_candidates(question, candidates, final_k=6)

    if not top_rows:
        return "Aucun contexte trouvé dans la base."

    context = build_context(top_rows)

    if no_llm:
        return (
            "=== CONTEXTE ===\n\n"
            + context
            + "\n\n[NO LLM] Mode forcé (--no-llm). Aucun appel LLM effectué."
        )

    answer = call_llm(question, context)

    if answer is None:
        return (
            "=== CONTEXTE ===\n\n"
            + context
            + "\n\n[NO LLM] Aucun LLM configuré ou appel impossible."
        )

    return (
        "=== CONTEXTE ===\n\n"
        + context
        + "\n\n=== RÉPONSE DU LLM ===\n\n"
        + answer
    )


# =========================
#  Main CLI
# =========================
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ask_pg.py \"your question\" [--no-llm] [--source=postgresql]")
        sys.exit(1)

    question = sys.argv[1]
    force_no_llm = "--no-llm" in sys.argv

    source = None
    for arg in sys.argv:
        if arg.startswith("--source="):
            source = arg.split("=")[1]

    result = ask_pg(question, no_llm=force_no_llm, source=source)
    print(result)


if __name__ == "__main__":
    main()

