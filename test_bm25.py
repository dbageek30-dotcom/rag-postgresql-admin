import os
from dotenv import load_dotenv
from agency.rag.rag_hybrid import RAGHybrid

# Charger automatiquement les variables d'environnement
load_dotenv()

db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

rag = RAGHybrid(db_params)

query = "wal checkpoint"
category = rag.detect_category(query)

results = rag.rule_search_bm25(query, category)

print("Catégorie détectée :", category)
print("Résultats BM25 :")
for r in results:
    print(f"- ID {r['id']} | score={r['score']:.4f}")

