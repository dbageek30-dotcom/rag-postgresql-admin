from agency.agents.toolsmith_pgbackrest import ToolsmithPgBackRest
from agency.agents.toolsmith_agent import ToolsmithAgent  # PostgreSQL

# RAG hybride
from agency.rag.rag_hybrid import RAGHybrid
from agency.llm.gemini_client import GeminiClient


class ToolOrchestrator:
    """
    Orchestrateur d’outils et de RAG.
    Reçoit une décision du Decision Layer et exécute l’action appropriée.
    """

    def execute(self, decision: dict):
        action = decision.get("action")
        args = decision.get("arguments", {})
        query = decision.get("query", "")  # important pour le RAG

        # ------------------------------------------------------------------
        # 1. pgBackRest
        # ------------------------------------------------------------------
        if action == "tool:pgbackrest":
            toolsmith = ToolsmithPgBackRest()
            result = toolsmith.generate_tool_for_command(args.get("command", "info"))

            namespace = {}
            exec(result["code"], namespace)

            ToolClass = namespace[result["class_name"]]
            tool = ToolClass(dry_run=False)

            return tool.run(args=args.get("options", {}))

        # ------------------------------------------------------------------
        # 2. PostgreSQL (via ToolsmithAgent)
        # ------------------------------------------------------------------
        if action == "tool:postgresql":
            toolsmith = ToolsmithAgent()
            result = toolsmith.generate_tool_for_command(args.get("command", ""))

            namespace = {}
            exec(result["code"], namespace)

            ToolClass = namespace[result["class_name"]]
            tool = ToolClass(dry_run=False)

            return tool.run(args=args.get("options", {}))

        # ------------------------------------------------------------------
        # 3. Patroni (placeholder)
        # ------------------------------------------------------------------
        if action == "tool:patroni":
            return {
                "error": "Tool Patroni non encore implémenté",
                "action": action
            }

        # ------------------------------------------------------------------
        # 4. RAG documentaire (hybride)
        # ------------------------------------------------------------------
        if action == "rag:doc":
            # Initialisation du RAG hybride
            rag = RAGHybrid({
                "dbname": "rag",
                "user": "rag_user",
                "password": "rag_password",
                "host": "localhost"
            })

            # Embedding de la requête
            llm = GeminiClient()
            query_embedding = llm.embed(query=query)

            # Exécution du pipeline RAG hybride
            return rag.query(query, query_embedding)

        # ------------------------------------------------------------------
        # 5. Raisonnement pur
        # ------------------------------------------------------------------
        if action == "reasoning-only":
            return {
                "reasoning": True,
                "message": "Pas d'action : reasoning-only."
            }

        # ------------------------------------------------------------------
        # 6. Fallback
        # ------------------------------------------------------------------
        return {
            "error": "Action inconnue",
            "action": action
        }

