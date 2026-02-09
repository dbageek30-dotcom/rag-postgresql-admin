import os
from dotenv import load_dotenv

from agency.agents.toolsmith_pgbackrest import ToolsmithPgBackRest
from agency.agents.toolsmith_agent import ToolsmithAgent  # PostgreSQL

from agency.rag.rag_hybrid import RAGHybrid
from agency.llm.ollama_client import OllamaClient


class ToolOrchestrator:
    """
    Orchestrateur d’outils et de RAG.
    Reçoit une décision du Decision Layer et exécute l’action appropriée.
    """

    def __init__(self):
        # Charger les variables d’environnement
        load_dotenv()

        self.db_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }

    def execute(self, decision: dict):
        action = decision.get("action")
        args = decision.get("arguments", {})
        query = decision.get("query", "")

        # ------------------------------------------------------------------
        # 1. pgBackRest
        # ------------------------------------------------------------------
        if action == "tool:pgbackrest":
            toolsmith = ToolsmithPgBackRest()
            result = toolsmith.generate_tool_for_command(
                args.get("command", "info")
            )

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
            result = toolsmith.generate_tool_for_command(
                args.get("command", "")
            )

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
            rag = RAGHybrid(self.db_params)

            # Embedding via Ollama
            llm = OllamaClient()
            query_embedding = llm.embed(query=query)

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

