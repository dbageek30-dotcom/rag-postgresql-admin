TOOL_TEMPLATE_POSTGRESQL = """
class {class_name}:
    def __init__(self, **kwargs):
        # On stocke tout : dbname, user, password, host, port, etc.
        self.config = kwargs

    def run(self):
        import psycopg2
        import subprocess
        from psycopg2.extras import RealDictCursor

        # --- MODE SQL ---
        if "{tool_type}" == "sql":
            query = {command_repr}
            try:
                # La connexion n'est créée qu'ici, au moment du run()
                conn = psycopg2.connect(
                    dbname=self.config.get("dbname"),
                    user=self.config.get("user"),
                    password=self.config.get("password"),
                    host=self.config.get("host"),
                    port=self.config.get("port")
                )
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)
                    result = cur.fetchall() if cur.description else {{"status": "success", "rows": cur.rowcount}}
                conn.close()
                return result
            except Exception as e:
                return {{"status": "error", "message": str(e)}}

        # --- MODE BINAIRE ---
        if "{tool_type}" == "binary":
            # Ici on pourrait construire la commande binaire si besoin
            cmd = ["{command}"]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return {{
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }}
            except Exception as e:
                return {{"status": "error", "message": str(e)}}
"""
