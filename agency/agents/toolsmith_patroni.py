# agency/agents/toolsmith_patroni.py

class ToolsmithPatroni:
    """
    Génère du code Python pour exécuter une commande Patroni.
    Compatible avec l'architecture Toolsmith → Worker.
    """

    def generate_tool_for_command(self, command: str) -> dict:
        """
        Exemple :
        - "status"
        - "list"
        - "failover --force"
        """

        class_name = "PatroniTool"

        code = f'''
import subprocess
import json

class {class_name}:
    def __init__(self, patroni_bin="/usr/bin/patronictl", config_file="/etc/patroni.yml"):
        self.patroni_bin = patroni_bin
        self.config_file = config_file

    def run(self, args=None):
        cmd = f"{{self.patroni_bin}} -c {{self.config_file}} {command}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            return {{
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }}
        except Exception as e:
            return {{"error": str(e)}}
'''

        return {
            "class_name": class_name,
            "code": code
        }

