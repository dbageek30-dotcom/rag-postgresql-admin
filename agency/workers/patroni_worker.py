# agency/workers/patroni_worker.py

import traceback

class PatroniWorker:
    """
    Worker Patroni :
    - reçoit une instruction structurée du manager
    - charge dynamiquement le tool généré par le Toolsmith Patroni
    - instancie le tool avec les paramètres SSH
    - exécute le tool (toujours binaire)
    - renvoie un résultat strict (JSON)
    """

    def __init__(self):
        pass

    def execute(self, instruction: dict) -> dict:
        try:
            if instruction.get("endpoint") != "/patroni":
                return {
                    "status": "error",
                    "error": "invalid_endpoint",
                    "details": f"PatroniWorker cannot handle endpoint {instruction.get('endpoint')}"
                }

            # Chargement dynamique du tool
            namespace = {}
            exec(instruction["tool_code"], namespace)

            ToolClass = namespace.get(instruction["tool_class"])
            if ToolClass is None:
                return {
                    "status": "error",
                    "error": "tool_class_not_found",
                    "details": f"Class {instruction['tool_class']} not found in tool_code"
                }

            # Payload = paramètres SSH
            payload = instruction.get("payload", {})

            # Instanciation du tool
            tool = ToolClass(**payload)

            # Exécution
            result = tool.run()

            return {
                "status": "ok",
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "error": "execution_failed",
                "details": str(e),
                "traceback": traceback.format_exc()
            }

