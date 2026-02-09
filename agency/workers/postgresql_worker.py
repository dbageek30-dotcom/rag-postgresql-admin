import json
import traceback

class PostgreSQLWorker:
    """
    Worker PostgreSQL :
    - reçoit une instruction structurée du manager
    - charge dynamiquement le tool généré par le Toolsmith
    - exécute le tool
    - renvoie un résultat strict (JSON)
    """

    def __init__(self, conn):
        self.conn = conn

    def execute(self, instruction: dict) -> dict:
        """
        Instruction attendue :
        {
            "endpoint": "/sql",
            "task": "execute_tool",
            "tool_class": "PgStatActivityTool",
            "tool_code": "class PgStatActivityTool: ...",
            "payload": { "limit": 50 }
        }
        """

        try:
            # 1. Vérification de l'endpoint
            if instruction.get("endpoint") != "/sql":
                return {
                    "status": "error",
                    "error": "invalid_endpoint",
                    "details": f"PostgreSQLWorker cannot handle endpoint {instruction.get('endpoint')}"
                }

            # 2. Charger dynamiquement le code du tool
            namespace = {}
            exec(instruction["tool_code"], namespace)

            ToolClass = namespace[instruction["tool_class"]]

            # 3. Instancier le tool
            tool = ToolClass(self.conn)

            # 4. Exécuter le tool
            payload = instruction.get("payload", {})
            result = tool.run(**payload)

            # 5. Retourner le résultat (déjà structuré par le tool)
            return result

        except Exception as e:
            return {
                "status": "error",
                "error": "execution_failed",
                "details": str(e),
                "traceback": traceback.format_exc()
            }

