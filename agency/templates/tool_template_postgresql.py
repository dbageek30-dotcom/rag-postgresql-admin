TOOL_TEMPLATE_POSTGRESQL = """
class {class_name}:
    \"""
    Tool PostgreSQL généré dynamiquement.
    - Mode SQL : utilise la connexion fournie par le worker (pas de reconnexion)
    - Mode binaire : exécute une commande PostgreSQL via SSH
    \"""

    def __init__(self, conn=None, ssh_host=None, ssh_user=None, ssh_key=None, **params):
        # Connexion SQL (fournie par le worker)
        self.conn = conn

        # Paramètres SSH pour les binaires
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key

        # Paramètres additionnels éventuels
        self.params = params

    def run(self):
        import subprocess
        from psycopg2.extras import RealDictCursor
        import shlex

        # -------------------------
        # MODE SQL
        # -------------------------
        if "{tool_type}" == "sql":
            query = {command_repr}

            if self.conn is None:
                return {"status": "error", "message": "Aucune connexion SQL fournie au tool."}

            try:
                with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)
                    if cur.description:
                        return cur.fetchall()
                    return {"status": "success", "rows": cur.rowcount}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # -------------------------
        # MODE BINAIRE
        # -------------------------
        if "{tool_type}" == "binary":
            if not self.ssh_host or not self.ssh_user or not self.ssh_key:
                return {"status": "error", "message": "Paramètres SSH manquants pour exécuter un binaire PostgreSQL."}

            # Commande complète générée par le Toolsmith
            base_cmd = shlex.split({command_repr})

            ssh_cmd = [
                "ssh",
                "-i", self.ssh_key,
                f"{self.ssh_user}@{self.ssh_host}",
                " ".join(base_cmd)
            ]

            try:
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                return {
                    "command": " ".join(ssh_cmd),
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
"""

