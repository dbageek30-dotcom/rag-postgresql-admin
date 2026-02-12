import json
import traceback

class PostgreSQLWorker:
    """
    Worker PostgreSQL :
    - reçoit une instruction structurée du manager
    - charge dynamiquement le tool généré par le Toolsmith
    - instancie le tool avec la connexion SQL ou les paramètres SSH
    - exécute le tool (SQL ou binaire)
    - renvoie un résultat strict (JSON)
    """

    def __init__(self, conn):
        # Connexion SQL persistante fournie par l'orchestrateur
        self.conn = conn

    def execute(self, instruction: dict) -> dict:
        try:
            # Vérification de l'endpoint
            if instruction.get("endpoint") != "/postgresql":
                return {
                    "status": "error",
                    "error": "invalid_endpoint",
                    "details": f"PostgreSQLWorker cannot handle endpoint {instruction.get('endpoint')}"
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

            # Récupération du payload
            payload = instruction.get("payload", {})

            # Instanciation du tool
            tool_type = instruction.get("tool_type")

            if tool_type == "sql":
                tool = ToolClass(conn=self.conn, **payload)
            else:
                tool = ToolClass(**payload)

            # Exécution du tool
            result = tool.run()

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

