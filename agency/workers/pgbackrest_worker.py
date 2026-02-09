import json
import subprocess

class PgBackRestWorker:
    """
    Worker pgBackRest dynamique :
    - ne dépend pas du .env
    - reçoit la VM cible dans tool_params
    - exécute le tool généré par le Toolsmith
    """

    def execute_tool(self, tool_class_code: str, tool_params: dict):
        """
        Exécute dynamiquement le code Python du tool généré.
        tool_params doit contenir :
            ssh_host, ssh_user, ssh_key, pgbackrest_bin
        """
        local_vars = {}
        try:
            exec(tool_class_code, {}, local_vars)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to load tool: {e}"
            }

        # Trouver la classe du tool
        tool_class = None
        for obj in local_vars.values():
            if isinstance(obj, type):
                tool_class = obj
                break

        if tool_class is None:
            return {
                "status": "error",
                "error": "No tool class found in generated code"
            }

        try:
            tool_instance = tool_class(**tool_params)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to instantiate tool: {e}"
            }

        try:
            result = tool_instance.run()
            return {
                "status": "ok",
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

