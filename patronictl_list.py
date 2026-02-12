from agency.rag.rag_hybrid import RAGHybrid
from agency.llm.ollama_client import OllamaClient
from agency.agents.toolsmith_patroni import ToolsmithPatroni
from agency.workers.patroni_worker import PatroniWorker
from sentence_transformers import SentenceTransformer
import os

# 1. Charger l’embedding model
embedder = SentenceTransformer(os.getenv("EMBEDDING_MODEL"))

# 2. Construire le RAG
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}
rag = RAGHybrid(db_params)

# 3. Construire le LLM Toolsmith (7B)
llm = OllamaClient(
    model=os.getenv("OLLAMA_MODEL_DEFAULT"),
    host=os.getenv("OLLAMA_HOST")
)

# 4. Construire le Toolsmith Patroni
toolsmith = ToolsmithPatroni(rag, llm)

# 5. Construire le Worker Patroni
worker = PatroniWorker()

# 6. Préparer la requête
action = "list"
context = {
    "version": "3.3.0",
    "cluster_name": "pgcluster"
}

query = f"patroni version {context['version']} commande pour action '{action}'"
embedding = embedder.encode(query)

# 7. Interroger le RAG
docs = rag.query(query, embedding)

# 8. Générer le tool
tool = toolsmith.generate_tool(action, {
    **context,
    "docs": docs
})

# 9. Préparer l’instruction Worker
worker_instruction = {
    "endpoint": "/patroni",
    "tool_type": tool["tool_type"],
    "tool_class": tool["tool_class"],
    "tool_code": tool["tool_code"],
    "payload": {
        "ssh_host": os.getenv("PATRONI_LEADER_HOST"),
        "ssh_user": os.getenv("PATRONI_LEADER_USER"),
        "ssh_key": os.getenv("PATRONI_LEADER_SSH_KEY")
    }
}

# 10. Exécuter
result = worker.execute(worker_instruction)
print(result)

