TOOL_TEMPLATE_PGBACKREST = """
import subprocess


class {class_name}:
    \"""
    Tool pgBackRest généré dynamiquement.

    - Exécute la commande pgBackRest '{command}'
    - Utilise SSH pour atteindre la VM distante
    - Supporte des options passées via **options
    \"""

    def __init__(self, ssh_host, ssh_user, ssh_key, pgbackrest_bin, **options):
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.pgbackrest_bin = pgbackrest_bin
        self.options = options

    def _build_command(self):
        base_cmd = [self.pgbackrest_bin, "{command}"]

        # Construction des options CLI à partir de self.options
        for key, value in self.options.items():
            cli_opt = f"--{{key.replace('_', '-')}}"
            if isinstance(value, bool):
                if value:
                    base_cmd.append(cli_opt)
            elif value is not None:
                base_cmd.extend([cli_opt, str(value)])

        ssh_cmd = [
            "ssh",
            "-i", self.ssh_key,
            f"{{self.ssh_user}}@{{self.ssh_host}}",
            " ".join(base_cmd)
        ]

        return ssh_cmd

    def run(self):
        cmd = self._build_command()

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {{
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }}
"""

