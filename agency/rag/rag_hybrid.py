import psycopg2
import numpy as np

from agency.llm.reranker_singleton import RerankerSingleton


class RAGHybrid:
    """
    Version RAG hybride améliorée :
    - filtrage par catégorie
    - vectoriel simple (pgvector)
    - règles simples
    - fusion naïve
    - reranking CrossEncoder (BAAI/bge-reranker-large)
    """

    def __init__(self, db_params):
        self.db_params = db_params
        self.reranker = RerankerSingleton.get_model()

    # ----------------------------------------------------------------------
    # Connexion PostgreSQL
    # ----------------------------------------------------------------------
    def _connect(self):
        return psycopg2.connect(**self.db_params)

    # ----------------------------------------------------------------------
    # 1. Filtrage par catégorie (statique)
    # ----------------------------------------------------------------------
    def detect_category(self, query: str) -> str:
        q = query.lower()

        if any(w in q for w in ["wal", "checkpoint", "replication", "table", "sql"]):
            return "postgresql"

        if any(w in q for w in ["stanza", "pgbackrest", "backup", "restore"]):
            return "pgbackrest"

        if any(w in q for w in ["patroni", "failover", "switchover", "replica"]):
            return "patroni"

        return "general"

    # ----------------------------------------------------------------------
    # 2. Recherche vectorielle simple
    # ----------------------------------------------------------------------
    def vector_search(self, query_embedding, category, top_k=5):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, content, metadata, source, version,
                   1 - (embedding <=> %s::vector) AS score
            FROM documents
            WHERE category = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (query_embedding, category, query_embedding, top_k))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {
                "id": r[0],
                "content": r[1],
                "metadata": r[2],
                "source": r[3],
                "version": r[4],
                "score": float(r[5])
            }
            for r in rows
        ]

    # ----------------------------------------------------------------------
    # 3. Recherche par règles simples
    # ----------------------------------------------------------------------
    def rule_search(self, query: str, category: str):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, content, metadata, source, version
            FROM documents
            WHERE category = %s
              AND content ILIKE %s
            LIMIT 5;
        """, (category, f"%{query}%"))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {
                "id": r[0],
                "content": r[1],
                "metadata": r[2],
                "source": r[3],
                "version": r[4],
                "score": 0.5
            }
            for r in rows
        ]

    # ----------------------------------------------------------------------
    # 4. Fusion naïve
    # ----------------------------------------------------------------------
    def merge_results(self, vector_results, rule_results):
        combined = vector_results + rule_results
        combined.sort(key=lambda x: x["score"], reverse=True)

        seen = set()
        unique_results = []
        for res in combined:
            if res["id"] not in seen:
                unique_results.append(res)
                seen.add(res["id"])

        return unique_results

    # ----------------------------------------------------------------------
    # 5. Reranking CrossEncoder
    # ----------------------------------------------------------------------
    def rerank(self, query, results, top_k=5):
        if not results:
            return []

        pairs = [(query, r["content"]) for r in results]
        scores = self.reranker.predict(pairs)

        scored = list(zip(scores, results))
        scored.sort(key=lambda x: x[0], reverse=True)

        return [r for (_, r) in scored[:top_k]]

    # ----------------------------------------------------------------------
    # 6. Pipeline complet
    # ----------------------------------------------------------------------
    def query(self, query: str, query_embedding):
        category = self.detect_category(query)

        vector_results = self.vector_search(query_embedding, category)
        rule_results = self.rule_search(query, category)

        merged = self.merge_results(vector_results, rule_results)

        if not merged:
            return {
                "fallback": True,
                "message": "Aucun document trouvé, fallback reasoning."
            }

        reranked = self.rerank(query, merged)

        return {
            "category": category,
            "results": reranked
        }

