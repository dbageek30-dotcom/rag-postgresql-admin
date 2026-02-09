from agency.agents.toolsmith_pgbackrest import ToolsmithPgBackRest
from agency.agents.toolsmith_agent import ToolsmithAgent  # PostgreSQL
# Patroni viendra plus tard

class ToolOrchestrator:
    """
    Version statique et pédagogique de l'orchestrateur d'outils.
    Il reçoit une décision du Decision Layer et exécute le tool approprié.
    """

    def execute(self, decision: dict):
        action = decision.get("action")
        args = decision.get("arguments", {})

        # 1. pgBackRest
        if action == "tool:pgbackrest":
            toolsmith = ToolsmithPgBackRest()
            result = toolsmith.generate_tool_for_command(args.get("command", "info"))

            namespace = {}
            exec(result["code"], namespace)

            ToolClass = namespace[result["class_name"]]
            tool = ToolClass(dry_run=False)

            return tool.run(args=args.get("options", {}))

        # 2. PostgreSQL (via ToolsmithAgent)
        if action == "tool:postgresql":
            toolsmith = ToolsmithAgent()
            result = toolsmith.generate_tool_for_command(args.get("command", ""))

            namespace = {}
            exec(result["code"], namespace)

            ToolClass = namespace[result["class_name"]]
            tool = ToolClass(dry_run=False)

            return tool.run(args=args.get("options", {}))

        # 3. Patroni (placeholder)
        if action == "tool:patroni":
            return {
                "error": "Tool Patroni non encore implémenté",
                "action": action
            }

        # 4. RAG documentaire
        if action == "rag:doc":
            return {
                "rag": True,
                "message": "Appeler le RAG documentaire ici."
            }

        # 5. Raisonnement pur
        if action == "reasoning-only":
            return {
                "reasoning": True,
                "message": "Pas d'action : reasoning-only."
            }

        # 6. Fallback
        return {
            "error": "Action inconnue",
            "action": action
        }

