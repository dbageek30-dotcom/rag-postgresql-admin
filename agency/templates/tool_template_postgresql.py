TOOL_TEMPLATE = """
class {class_name}:
    \"\"\"
    Tool auto-généré par le toolsmith PostgreSQL.
    type: {tool_type}   # "sql" ou "binary"
    command: {command}  # commande SQL ou binaire
    \"\"\"

    def __init__(self, conn=None):
        self.conn = conn

    def run(self, **kwargs):
        # Commande SQL
        if "{tool_type}" == "sql":
            sql = f\"\"\"{command}\"\"\"
            cur = self.conn.cursor()
            cur.execute(sql, kwargs)
            try:
                rows = cur.fetchall()
            except:
                rows = None
            cur.close()
            return rows

        # Commande binaire
        if "{tool_type}" == "binary":
            import subprocess
            cmd = ["{command}"] + [str(v) for v in kwargs.values()]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
"""

