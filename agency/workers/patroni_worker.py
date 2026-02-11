# agency/workers/patroni_worker.py

import subprocess
import tempfile
import json
import os

class PatroniWorker:
    def __init__(self, params=None):
        self.params = params or {}

    def execute_tool(self, code: str, params: dict):
        # 1. Préparation sécurisée des options pour l'injection
        # On récupère les options et on s'assure qu'elles sont traitées comme un dict Python
        options_dict = params.get("options", {})

        # On génère le code en utilisant repr() pour que True devienne True et non true
        injected_code = code + f'''
import json

options = {repr(options_dict)}

tool = PatroniTool(
    patroni_bin="{params["patroni_bin"]}",
    config_file="{params["config_file"]}",
    **options
)

print(json.dumps(tool.run()))
'''

        # 2. Écriture du script temporaire
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(injected_code)
            f.flush()
            local_path = f.name

        remote_path = "/tmp/patroni_tool_exec.py"

        try:
            # 3. Transfert SCP
            subprocess.run(
                ["scp", "-i", params["ssh_key"], "-o", "StrictHostKeyChecking=no",
                 local_path, f"{params['ssh_user']}@{params['ssh_host']}:{remote_path}"],
                check=True, capture_output=True
            )

            # 4. Exécution SSH
            cmd = [
                "ssh", "-i", params["ssh_key"], "-o", "StrictHostKeyChecking=no",
                f"{params['ssh_user']}@{params['ssh_host']}",
                f"python3 {remote_path}"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Nettoyage distant
            subprocess.run(["ssh", "-i", params["ssh_key"], f"{params['ssh_user']}@{params['ssh_host']}", f"rm {remote_path}"], capture_output=True)

            try:
                return json.loads(result.stdout)
            except:
                return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}

        finally:
            if os.path.exists(local_path):
                os.remove(local_path)
