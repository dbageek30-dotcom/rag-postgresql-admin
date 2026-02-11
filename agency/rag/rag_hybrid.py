import psycopg2
import os
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
    # 3b. Recherche lexicale BM25 (tsvector)
    # ----------------------------------------------------------------------
    def rule_search_bm25(self, query: str, category: str, top_k=5):
        conn = self._connect()
        cur = conn.cursor()

        # Conversion de la requête en tsquery
        cur.execute("""
            SELECT id, content, metadata, source, version,
                   ts_rank(tsv, plainto_tsquery(%s)) AS score
            FROM documents
            WHERE category = %s
              AND tsv @@ plainto_tsquery(%s)
            ORDER BY score DESC
            LIMIT %s;
        """, (query, category, query, top_k))

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
    # Fusion hybride vector + BM25 (100% dynamique)
    # ----------------------------------------------------------------------
    def merge_results_hybrid(self, vector_results, bm25_results):
        # Lire les pondérations depuis .env
        w_vec = float(os.getenv("RAG_WEIGHT_VECTOR", 0.7))
        w_bm25 = float(os.getenv("RAG_WEIGHT_BM25", 0.3))

        # Normalisation générique
        def normalize(scores):
            if not scores:
                return []
            max_s = max(scores)
            min_s = min(scores)
            if max_s == min_s:
                return [1.0 for _ in scores]
            return [(s - min_s) / (max_s - min_s) for s in scores]

        # Normaliser vector
        vec_scores = normalize([r["score"] for r in vector_results])
        for r, s in zip(vector_results, vec_scores):
            r["hybrid_score"] = s * w_vec

        # Normaliser BM25
        bm25_scores = normalize([r["score"] for r in bm25_results])
        for r, s in zip(bm25_results, bm25_scores):
            r["hybrid_score"] = s * w_bm25

        # Fusion + déduplication
        combined = vector_results + bm25_results
        unique = {}
        for r in combined:
            rid = r["id"]
            if rid not in unique or r["hybrid_score"] > unique[rid]["hybrid_score"]:
                unique[rid] = r

        # Tri final
        return sorted(unique.values(), key=lambda x: x["hybrid_score"], reverse=True)


    # ----------------------------------------------------------------------
    # 5. Reranking CrossEncoder
    # ----------------------------------------------------------------------
    def rerank(self, query, results):
        if not results:
            return []

        # Nombre de résultats à garder après reranking
        top_k = int(os.getenv("RAG_RERANK_TOP_K", 5))

        # Préparer les paires (query, chunk)
        pairs = [(query, r["content"]) for r in results]

        # Scores du CrossEncoder
        scores = self.reranker.predict(pairs)

        # Ajouter un score normalisé
        min_s = min(scores)
        max_s = max(scores)
        norm_scores = [
            (s - min_s) / (max_s - min_s) if max_s > min_s else 1.0
            for s in scores
        ]

        for r, s, ns in zip(results, scores, norm_scores):
            r["rerank_raw"] = float(s)
            r["rerank_score"] = float(ns)

        # Trier par score normalisé
        results = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

        return results[:top_k]

    # ----------------------------------------------------------------------
    # 6. Pipeline complet
    # ----------------------------------------------------------------------

    def query(self, query: str, query_embedding):
        # Lire les options dynamiques
        use_bm25 = os.getenv("RAG_USE_BM25", "true").lower() == "true"
        use_hybrid = os.getenv("RAG_USE_HYBRID", "true").lower() == "true"
        top_k = int(os.getenv("RAG_TOP_K", 5))

        # 1. Détection de catégorie
        category = self.detect_category(query)

        # 2. Recherche vectorielle
        vector_results = self.vector_search(query_embedding, category, top_k=top_k)

        # 3. Recherche lexicale (BM25 ou fallback ILIKE)
        if use_bm25:
            bm25_results = self.rule_search_bm25(query, category)
        else:
            bm25_results = self.rule_search(query, category)

        # 4. Fusion
        if use_hybrid:
            merged = self.merge_results_hybrid(vector_results, bm25_results)
        else:
            merged = self.merge_results(vector_results, bm25_results)

        # 5. Fallback si aucun résultat
        if not merged:
            return {
                "fallback": True,
                "message": "Aucun document trouvé, fallback reasoning."
            }

        # 6. Reranking final
        reranked = self.rerank(query, merged)

        # 7. Fallback intelligent basé sur le score du reranker
        min_conf = float(os.getenv("RAG_MIN_CONFIDENCE", 0.25))
        best_score = reranked[0].get("rerank_score", 0.0)

        if best_score < min_conf:
            return {
                "fallback": True,
                "message": "Les documents trouvés sont peu pertinents, je préfère raisonner sans les utiliser.",
                "category": category,
                "results": reranked
            }

        # 8. Résultat normal
        return {
            "category": category,
            "results": reranked
        }

