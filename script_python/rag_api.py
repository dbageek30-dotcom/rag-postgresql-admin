from fastapi import FastAPI
from pydantic import BaseModel
from script_python.ask_pg import ask_pg

app = FastAPI(
    title="PG AI Agency API",
    description="API pour interroger le pipeline RAG PostgreSQL multi-sources",
    version="0.2.0"
)

class Query(BaseModel):
    question: str
    no_llm: bool = False
    source: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

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

