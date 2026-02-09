class DecisionLayer:
    """
    Version statique et pédagogique du Decision Layer.
    Elle analyse une requête et renvoie :
    - l'action à effectuer
    - la raison de la décision
    - les arguments extraits (si applicable)
    """

    def decide(self, query: str) -> dict:
        q = query.lower().strip()

        # 1. Requêtes pgBackRest
        if "backup" in q or "pgbackrest" in q or "stanza" in q:
            return {
                "action": "tool:pgbackrest",
                "reason": "La requête concerne une opération pgBackRest.",
                "arguments": {}
            }

        # 2. Requêtes PostgreSQL
        if any(word in q for word in ["sql", "table", "index", "query", "select", "insert"]):
            return {
                "action": "tool:postgresql",
                "reason": "La requête concerne une opération SQL/PostgreSQL.",
                "arguments": {}
            }

        # 3. Requêtes Patroni
        if "patroni" in q or "failover" in q or "switchover" in q:
            return {
                "action": "tool:patroni",
                "reason": "La requête concerne la gestion du cluster Patroni.",
                "arguments": {}
            }

        # 4. Requêtes documentaires (RAG)
        if any(word in q for word in ["explain", "documentation", "how to", "comment", "guide"]):
            return {
                "action": "rag:doc",
                "reason": "La requête semble demander une explication/documentation.",
                "arguments": {}
            }

        # 5. Raisonnement pur
        if len(q.split()) < 4:
            return {
                "action": "reasoning-only",
                "reason": "Requête courte ou ambiguë, mieux vaut raisonner avant d'agir.",
                "arguments": {}
            }

        # 6. Fallback
        return {
            "action": "rag:doc",
            "reason": "Cas général : on passe par le RAG documentaire.",
            "arguments": {}
        }

