from fastapi import FastAPI
from .rag import rag_query
from .db import SOURCE_VERSION_MAP

app = FastAPI(title="PostgreSQL Admin RAG API")

@app.get("/health")
def health():
    return {"status": "ok"}

# Query générique (sans filtrage)
@app.get("/query")
def query(q: str):
    return rag_query(q)

# Liste dynamique des sources et versions
@app.get("/sources")
def sources():
    return {
        "sources": [
            {"name": src, "version": ver}
            for src, ver in SOURCE_VERSION_MAP.items()
        ]
    }

# Endpoints spécialisés
@app.get("/query/postgresql")
def query_postgresql(q: str):
    version = SOURCE_VERSION_MAP.get("postgresql")
    return rag_query(q, source="postgresql", version=version)

@app.get("/query/pgbackrest")
def query_pgbackrest(q: str):
    version = SOURCE_VERSION_MAP.get("pgbackrest")
    return rag_query(q, source="pgbackrest", version=version)

@app.get("/query/patroni")
def query_patroni(q: str):
    version = SOURCE_VERSION_MAP.get("patroni")
    return rag_query(q, source="patroni", version=version)

# Agent manager (routing intelligent)
@app.get("/query/agent")
def query_agent(q: str):
    q_lower = q.lower()

    # pgBackRest
    if any(word in q_lower for word in ["backup", "restore", "pgbackrest", "archive", "repo"]):
        version = SOURCE_VERSION_MAP.get("pgbackrest")
        return rag_query(q, source="pgbackrest", version=version)

    # Patroni
    if any(word in q_lower for word in ["patroni", "failover", "replica", "leader", "ha"]):
        version = SOURCE_VERSION_MAP.get("patroni")
        return rag_query(q, source="patroni", version=version)

    # Par défaut → PostgreSQL
    version = SOURCE_VERSION_MAP.get("postgresql")
    return rag_query(q, source="postgresql", version=version)

