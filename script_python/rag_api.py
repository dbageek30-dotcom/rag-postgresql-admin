from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from ask_pg import ask_pg
from dotenv import load_dotenv

# =========================
#  Charger la configuration
# =========================
load_dotenv()

API_TITLE = "PG AI Agency API"
API_DESC = "API pour interroger le pipeline RAG PostgreSQL multi-sources"
API_VERSION = "1.0.0"

app = FastAPI(
    title=API_TITLE,
    description=API_DESC,
    version=API_VERSION
)

# =========================
#  CORS (optionnel)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
#  Modèles Pydantic
# =========================
class Query(BaseModel):
    question: str
    no_llm: bool = False
    source: str | None = None


# =========================
#  Endpoints
# =========================

@app.get("/health")
def health():
    return {"status": "ok", "llm_provider": os.getenv("LLM_PROVIDER", "none")}


@app.post("/ask")
def ask(payload: Query):
    answer = ask_pg(
        payload.question,
        no_llm=payload.no_llm,
        source=payload.source
    )
    return {
        "question": payload.question,
        "source": payload.source,
        "answer": answer
    }


@app.get("/sources")
def list_sources():
    """
    Retourne la liste des sources disponibles dans la base.
    """
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT source FROM documents ORDER BY source;")
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"sources": rows}


@app.get("/versions/{source}")
def list_versions(source: str):
    """
    Retourne les versions disponibles pour une source donnée.
    """
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT version FROM documents WHERE source = %s ORDER BY version;",
        (source,)
    )
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"source": source, "versions": rows}


@app.get("/debug/chunks")
def debug_chunks(limit: int = 10):
    """
    Permet d'inspecter les premiers chunks (debug).
    """
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT source, version, metadata->>'title', metadata->>'html_id', LEFT(content, 200)
        FROM documents
        LIMIT %s;
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    chunks = []
    for src, ver, title, html_id, snippet in rows:
        chunks.append({
            "source": src,
            "version": ver,
            "title": title,
            "html_id": html_id,
            "snippet": snippet
        })

    return {"chunks": chunks}

