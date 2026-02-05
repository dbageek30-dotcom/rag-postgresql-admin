from fastapi import FastAPI
from .rag import rag_query

app = FastAPI(title="PostgreSQL Admin RAG API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/query")
def query(q: str, k: int = 5):
    results = rag_query(q, k)
    return {"query": q, "results": results}

@app.get("/sources")
def sources():
    return {
        "sources": [
            {"name": "postgresql", "version": "18.1"},
            {"name": "patroni", "version": "4.1.0"},
            {"name": "pgbackrest", "version": "2.58.0"},
        ]
    }

