# agency/agents/toolsmith_patroni.py

class ToolsmithPatroni:
    """
    Génère du code Python pour exécuter une commande Patroni via patronictl.
    Le Worker injecte patroni_bin et patroni_config.
    """

    def generate_tool_for_command(self, command: str) -> dict:
        class_name = "PatroniTool"

        code = f'''
import subprocess
import json

class {class_name}:
    def __init__(self, patroni_bin, config_file):
        self.patroni_bin = patroni_bin
        self.config_file = config_file

    def run(self):
        cmd = f"{{self.patroni_bin}} -c {{self.config_file}} {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {{
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }}
'''

        return {
            "class_name": class_name,
            "code": code
        }

