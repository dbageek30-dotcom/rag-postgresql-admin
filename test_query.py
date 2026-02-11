import os
from dotenv import load_dotenv
from agency.rag.rag_hybrid import RAGHybrid
from agency.llm.embedding_singleton import EmbeddingSingleton

# Charger les variables d'environnement
load_dotenv()

# Connexion DB dynamique
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# Initialiser RAG
rag = RAGHybrid(db_params)

# Embedding dynamique
embedder = EmbeddingSingleton.get_model()

query = "comment fonctionne le checkpoint dans PostgreSQL ?"
query_embedding = embedder.encode(query).tolist()

# Appel dynamique du pipeline
response = rag.query(query, query_embedding)

print("Catégorie détectée :", response.get("category"))
print("Résultats :")
for r in response.get("results", []):
    print(
        f"- ID {r['id']} | "
        f"hybrid={r.get('hybrid_score')} | "
        f"rerank_raw={r.get('rerank_raw')} | "
        f"rerank_score={r.get('rerank_score')}"
    )

