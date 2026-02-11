# agency/workers/pgbackrest_worker.py
import json
import subprocess

class PgBackRestWorker:
    def execute_tool(self, tool_class_code: str, tool_params: dict):
        # On extrait les options pour ne pas les mélanger aux paramètres SSH de base
        # On utilise .copy() pour ne pas modifier l'original dans l'orchestrateur
        params = tool_params.copy()
        options = params.pop("options", {})
        
        local_vars = {}
        try:
            # On exécute le code du template pour définir la classe en mémoire
            exec(tool_class_code, {}, local_vars)
        except Exception as e:
            return {"status": "error", "error": f"Failed to load tool: {e}"}

        # On récupère la classe générée
        tool_class = next((obj for obj in local_vars.values() if isinstance(obj, type)), None)

        if tool_class is None:
            return {"status": "error", "error": "No tool class found"}

        try:
            # Instanciation : params contient ssh_host, user, key, bin
            # options contient stanza, type, etc.
            tool_instance = tool_class(**params, **options)
            
            # Exécution (qui lance le subprocess.run(ssh ...))
            result = tool_instance.run()
            
            return {
                "status": "ok",
                "result": result
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
