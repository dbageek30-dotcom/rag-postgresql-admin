from agency.decision.decision_layer import DecisionLayer
from agency.decision.tool_orchestrator import ToolOrchestrator
from agency.decision.llm_manager import LLMManager   # ← AJOUT


class DBAManager:
    """
    Le cerveau du système :
    - reçoit une requête utilisateur
    - demande une décision au DecisionLayer
    - si aucun endpoint → LLM Manager 32B
    - appelle l'Orchestrator
    - interprète le résultat
    """

    def __init__(self):
        self.decision_layer = DecisionLayer()
        self.orchestrator = ToolOrchestrator()
        self.llm_manager = LLMManager()  # ← AJOUT

    def handle(self, query: str):
        """
        Point d'entrée principal.
        """
        # 1. Décision stricte (endpoints)
        decision = self.decision_layer.decide(query)

        # 2. Si pas d’endpoint explicite → LLM Manager 32B
        if decision["action"] == "rag:doc" and decision["reason"].startswith("No explicit endpoint"):
            routed = self.llm_manager.route(query)

            if routed["type"] == "doc":
                # On reste dans le pipeline documentaire
                decision = {
                    "action": "rag:doc",
                    "payload": routed["payload"],
                    "arguments": routed.get("arguments", {})
                }
            else:
                # Action → ToolOrchestrator
                decision = {
                    "action": f"tool:{routed['action']}",
                    "payload": routed["payload"],
                    "arguments": routed.get("arguments", {})
                }

        # 3. Appel de l'Orchestrator
        result = self.orchestrator.execute({
            "action": decision.get("action"),
            "payload": decision.get("payload", ""),
            "arguments": decision.get("arguments", {})
        })

        # 4. Interprétation simple
        return self._interpret_result(decision.get("action"), result)

    def _interpret_result(self, action: str, result: dict):
        """
        Interprétation minimale :
        - si erreur → renvoyer proprement
        - si succès → renvoyer le résultat brut
        """
        if "error" in result:
            return {
                "status": "error",
                "action": action,
                "message": result["error"]
            }

        return {
            "status": "ok",
            "action": action,
            "result": result
        }

