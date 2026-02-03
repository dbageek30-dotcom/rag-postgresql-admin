#!/usr/bin/env python3
import sys
import json
import textwrap
import psycopg2
import requests

from sentence_transformers import SentenceTransformer, CrossEncoder

# =========================
#  Modèles embeddings + reranker
# =========================
EMBED_MODEL_NAME = "BAAI/bge-base-en-v1.5"
RERANK_MODEL_NAME = "BAAI/bge-reranker-large"

embed_model = SentenceTransformer(EMBED_MODEL_NAME)
reranker = CrossEncoder(RERANK_MODEL_NAME)

# =========================
#  Config PostgreSQL
# =========================
PG_CONN_INFO = {
    "host": "localhost",
    "port": 5432,
    "dbname": "rag",
    "user": "postgres",
    "password": "postgres"  # adapte si besoin
}

# =========================
#  Config LLM (Qwen local via Ollama ou autre)
# =========================
LLM_URL = "http://10.214.0.8:11434/api/chat"  # adapte à ton endpoint
LLM_MODEL = "qwen2.5:7b-instruct-q4_K_M"                     # adapte au nom de ton modèle


def get_embedding(text: str):
    # BGE conseille la normalisation
    return embed_model.encode(text, normalize_embeddings=True).tolist()


def fetch_candidates(question: str, top_k: int = 30):
    emb = get_embedding(question)

    conn = psycopg2.connect(**PG_CONN_INFO)
    cur = conn.cursor()

    # top_k candidats purement vectoriels
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


def rerank_candidates(question: str, rows, final_k: int = 6):
    if not rows:
        return []

    # paires (question, chunk)
    pairs = [(question, content) for (_, _, content, _) in rows]
    scores = reranker.predict(pairs)

    scored = list(zip(scores, rows))
    scored.sort(key=lambda x: x[0], reverse=True)

    return [r for (_, r) in scored[:final_k]]


def build_context(reranked_rows):
    parts = []
    for title, html_id, content, distance in reranked_rows:
        # on tronque un peu le contenu pour éviter un contexte monstrueux
        snippet = textwrap.shorten(content.replace("\n", " "), width=1200, placeholder=" ...")
        parts.append(f"### {title} ({html_id})\n{snippet}\n")
    return "\n\n".join(parts)


def call_llm(question: str, context: str) -> str:
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

    resp = requests.post(LLM_URL, json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()

    # adapte selon le format de retour de ton endpoint
    if isinstance(data, dict) and "message" in data:
        return data["message"]["content"]
    elif isinstance(data, dict) and "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        return str(data)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ask_pg.py \"your question\"")
        sys.exit(1)

    question = sys.argv[1]

    print(f"Question: {question}\n")

    # 1) candidats vectoriels
    candidates = fetch_candidates(question, top_k=30)

    # 2) reranking cross-encoder
    top_rows = rerank_candidates(question, candidates, final_k=6)

    if not top_rows:
        print("Aucun contexte trouvé dans la base.")
        sys.exit(0)

    # 3) construction du contexte
    context = build_context(top_rows)

    print("=== CONTEXTE ENVOYÉ AU LLM ===\n")
    print(context)
    print("\n=== RÉPONSE DU LLM (Qwen local) ===\n")

    # 4) appel LLM
    answer = call_llm(question, context)
    print(answer)


if __name__ == "__main__":
    main()

