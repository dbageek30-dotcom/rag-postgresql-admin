TOOL_TEMPLATE_POSTGRESQL = """
class {class_name}:
    \"\"\"
    Tool auto-généré pour PostgreSQL.
    Type: {tool_type}
    \"\"\"

    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def run(self, **kwargs):
        import subprocess
        import psycopg2
        from psycopg2.extras import RealDictCursor

        # --- LOGIQUE SQL ---
        if "{tool_type}" == "sql":
            query = {command_repr}
            try:
                # Connexion utilisant uniquement les paramètres injectés
                conn = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port
                )
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, kwargs)
                    if cur.description:
                        result = cur.fetchall()
                    else:
                        conn.commit()
                        result = {{"status": "success", "rowcount": cur.rowcount}}
                conn.close()
                return result
            except Exception as e:
                return {{"status": "error", "message": str(e)}}

        # --- LOGIQUE BINAIRE ---
        if "{tool_type}" == "binary":
            # Exécution brute de la commande telle quelle
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
