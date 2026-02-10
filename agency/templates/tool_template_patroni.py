TOOL_TEMPLATE_PATRONI = """
class {class_name}:
    \"""
    Tool Patroni généré dynamiquement.
    \"""

    def __init__(self, ssh_host, ssh_user, ssh_key, patroni_bin, config_file, **options):
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.patroni_bin = patroni_bin
        self.config_file = config_file
        self.options = options

    def _build_command(self):
        # Commande de base patronictl
        base_cmd = [self.patroni_bin, "-c", self.config_file, "{command}"]

        # Ajout dynamique des options
        for key, value in self.options.items():
            cli_opt = f"--{key.replace('_', '-')}"
            if isinstance(value, bool):
                if value:
                    base_cmd.append(cli_opt)
            elif value is not None:
                base_cmd.extend([cli_opt, str(value)])

        # Construction de la commande SSH distante
        ssh_cmd = [
            "ssh",
            "-i", self.ssh_key,
            f"{self.ssh_user}@{self.ssh_host}",
            " ".join(base_cmd)
        ]
        return ssh_cmd

    def run(self):
        import subprocess

        cmd = self._build_command()
        result = subprocess.run(cmd, capture_output=True, text=True)

        return {{
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }}
"""

