TOOL_TEMPLATE_PATRONI = """
class {class_name}:
    \"""
    Tool Patroni généré dynamiquement.
    Exécuté localement sur la VM cible via le Worker.
    \"""

    def __init__(self, patroni_bin, config_file, **options):
        self.patroni_bin = patroni_bin
        self.config_file = config_file
        self.options = options

    def _build_command(self):
        base_cmd = [self.patroni_bin, "-c", self.config_file, "{command}"]

        for key, value in self.options.items():
            cli_opt = f"--{key.replace('_', '-')}"
            if isinstance(value, bool):
                if value:
                    base_cmd.append(cli_opt)
            elif value is not None:
                base_cmd.extend([cli_opt, str(value)])

        return base_cmd

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

