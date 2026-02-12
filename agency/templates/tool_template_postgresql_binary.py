TOOL_TEMPLATE_POSTGRESQL_BINARY = """
class {class_name}:
    \"""
    Tool PostgreSQL binaire généré dynamiquement.
    Exécute une commande PostgreSQL via SSH.
    \"""

    def __init__(self, ssh_host=None, ssh_user=None, ssh_key=None, **params):
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.params = params

    def run(self):
        import subprocess
        import shlex

        if not self.ssh_host or not self.ssh_user or not self.ssh_key:
            return {{"status": "error", "message": "Paramètres SSH manquants pour exécuter un binaire PostgreSQL."}}

        base_cmd = shlex.split({command_repr})

        ssh_cmd = [
            "ssh",
            "-i", self.ssh_key,
            f"{self.ssh_user}@{self.ssh_host}",
            " ".join(base_cmd)
        ]

        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            return {{
                "command": " ".join(ssh_cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }}
        except Exception as e:
            return {{"status": "error", "message": str(e)}}
"""

