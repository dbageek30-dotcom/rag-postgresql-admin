# agency/workers/patroni_worker.py

import subprocess
import tempfile
import json

class PatroniWorker:
    """
    Exécute patronictl sur la machine distante via SSH.
    Identique à PgBackRestWorker mais adapté à Patroni.
    """

    def __init__(self, params):
        self.params = params

    def execute_tool(self, code: str, params: dict):
        # Injecter les paramètres dans le script
        injected_code = code + f'''

tool = PatroniTool("{params["patroni_bin"]}", "{params["patroni_config"]}")
print(json.dumps(tool.run()))
'''

        # 1. Écrire le script localement
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(injected_code)
            f.flush()
            local_path = f.name

        remote_path = "/tmp/patroni_tool_exec.py"

        # 2. Copier sur la VM distante
        subprocess.run(
            ["scp", "-i", params["ssh_key"], "-o", "StrictHostKeyChecking=no",
             local_path, f"{params['ssh_user']}@{params['ssh_host']}:{remote_path}"],
            check=True
        )

        # 3. Exécuter sur la VM distante
        cmd = [
            "ssh", "-i", params["ssh_key"], "-o", "StrictHostKeyChecking=no",
            f"{params['ssh_user']}@{params['ssh_host']}",
            f"python3 {remote_path}"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

