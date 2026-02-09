class DecisionLayer:
    """
    Decision Layer STRICT :
    - aucune interprétation
    - aucun langage naturel
    - uniquement des endpoints explicites
    - fallback documentaire sécurisé
    """

    def decide(self, query: str) -> dict:
        q = query.strip()

        # ------------------------------------------------------------
        # 1. Endpoints explicites (priorité absolue)
        # ------------------------------------------------------------
        if q.startswith("/sql"):
            return {
                "action": "tool:postgresql",
                "reason": "Explicit /sql endpoint.",
                "payload": q[len("/sql"):].strip()
            }

        if q.startswith("/tool"):
            return {
                "action": "tool:pgbackrest",
                "reason": "Explicit /tool endpoint.",
                "payload": q[len("/tool"):].strip()
            }

        if q.startswith("/patroni"):
            return {
                "action": "tool:patroni",
                "reason": "Explicit /patroni endpoint.",
                "payload": q[len("/patroni"):].strip()
            }

        if q.startswith("/doc"):
            return {
                "action": "rag:doc",
                "reason": "Explicit /doc endpoint.",
                "payload": q[len("/doc"):].strip()
            }

        # ------------------------------------------------------------
        # 2. Aucun endpoint → fallback documentaire
        #    (utile uniquement pour toi, niveau “moi”)
        # ------------------------------------------------------------
        return {
            "action": "rag:doc",
            "reason": "No explicit endpoint. Defaulting to documentation RAG.",
            "payload": q
        }

