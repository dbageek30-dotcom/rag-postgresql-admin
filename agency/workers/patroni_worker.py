# agency/workers/patroni_worker.py

import subprocess
import tempfile
import json
import os

class PatroniWorker:
    """
    Exécute un outil Patroni généré dynamiquement sur une VM distante.
    Process : SCP du script généré -> SSH python3 execution -> Nettoyage.
    """

    def __init__(self, params=None):
        # On peut stocker des params par défaut si besoin
        self.params = params or {}

    def execute_tool(self, code: str, params: dict):
        """
        code: Le code de la classe généré par le Toolsmith
        params: Dictionnaire contenant ssh_host, ssh_user, ssh_key, patroni_bin, config_file
        """
        # 1. Injecter l'instanciation et l'appel à .run() à la fin du code généré
        # On utilise PatroniTool car c'est le nom de classe par défaut du ToolsmithPatroni
        injected_code = code + f'''
import json

tool = PatroniTool(
    patroni_bin="{params["patroni_bin"]}",
    config_file="{params["config_file"]}",
    **{json.dumps(params.get("options", {}))}
)

print(json.dumps(tool.run()))
'''

        # 2. Écrire le script complet dans un fichier temporaire local
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(injected_code)
            f.flush()
            local_path = f.name

        remote_path = "/tmp/patroni_tool_exec.py"

        try:
            # 3. SCP : Envoyer le script sur la VM distante
            subprocess.run(
                [
                    "scp", "-i", params["ssh_key"], 
                    "-o", "StrictHostKeyChecking=no",
                    local_path, 
                    f"{params['ssh_user']}@{params['ssh_host']}:{remote_path}"
                ],
                check=True, capture_output=True
            )

            # 4. SSH : Exécuter le script sur la VM distante
            cmd = [
                "ssh", "-i", params["ssh_key"], 
                "-o", "StrictHostKeyChecking=no",
                f"{params['ssh_user']}@{params['ssh_host']}",
                f"python3 {remote_path}"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 5. Nettoyage distant (optionnel mais propre)
            subprocess.run([
                "ssh", "-i", params["ssh_key"], 
                f"{params['ssh_user']}@{params['ssh_host']}", 
                f"rm {remote_path}"
            ], capture_output=True)

            # On essaie de parser le JSON retourné par le script distant
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }

        finally:
            # Nettoyage du fichier temporaire local
            if os.path.exists(local_path):
                os.remove(local_path)
