import json
import traceback

class PostgreSQLWorker:
    """
    Worker PostgreSQL :
    - reçoit une instruction structurée du manager
    - charge dynamiquement le tool généré par le Toolsmith
    - exécute le tool (SQL ou binaire)
    - renvoie un résultat strict (JSON)
    """

    def __init__(self, conn):
        self.conn = conn

    def execute(self, instruction: dict) -> dict:
        try:
            if instruction.get("endpoint") != "/postgresql":
                return {
                    "status": "error",
                    "error": "invalid_endpoint",
                    "details": f"PostgreSQLWorker cannot handle endpoint {instruction.get('endpoint')}"
                }

            namespace = {}
            exec(instruction["tool_code"], namespace)
            ToolClass = namespace[instruction["tool_class"]]

            try:
                tool = ToolClass(self.conn)
            except TypeError:
                tool = ToolClass()

            payload = instruction.get("payload", {})
            result = tool.run(**payload)

            return {
                "status": "ok",
                "result": result
            }

        except Exception as e:
            # rollback obligatoire si SQL a échoué
            try:
                self.conn.rollback()
            except:
                pass

            return {
                "status": "error",
                "error": "execution_failed",
                "details": str(e),
                "traceback": traceback.format_exc()
            }

