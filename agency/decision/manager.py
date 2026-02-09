from agency.decision.decision_layer import DecisionLayer
from agency.decision.tool_orchestrator import ToolOrchestrator


class DBAManager:
    """
    Le cerveau du système :
    - reçoit une requête utilisateur
    - demande une décision au DecisionLayer
    - appelle l'Orchestrator
    - interprète le résultat
    - reboucle si nécessaire
    """

    def __init__(self):
        self.decision_layer = DecisionLayer()
        self.orchestrator = ToolOrchestrator()

    def handle(self, query: str):
        """
        Point d'entrée principal.
        """
        # 1. Décision
        decision = self.decision_layer.decide(query)

        # 2. Préparation du payload
        action = decision.get("action")
        payload = decision.get("payload", "")
        args = decision.get("arguments", {})

        # 3. Appel de l'Orchestrator
        result = self.orchestrator.execute({
            "action": action,
            "payload": payload,
            "arguments": args
        })

        # 4. Interprétation simple
        return self._interpret_result(action, result)

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

