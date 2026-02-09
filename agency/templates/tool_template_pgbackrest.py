TOOL_TEMPLATE_PGBACKREST = """
class {class_name}:
    def __init__(self, host="10.210.0.2", user="postgres", dry_run=False):
        self.host = host
        self.user = user
        self.dry_run = dry_run

    def run(self, args=None):
        import subprocess, json

        base_cmd = ["pgbackrest", "{command}"]

        if args:
            for k, v in args.items():
                if isinstance(v, bool):
                    if v:
                        # On veut que le code généré soit : f"--{{k}}"
                        base_cmd.append(f"--{{k}}")
                else:
                    # On veut que le code généré soit : f"--{{k}}={{v}}"
                    base_cmd.append(f"--{{k}}={{v}}")

        # Ici, on veut que le code final contienne de vraies f-strings exploitables
        ssh_cmd = ["ssh", f"{{self.user}}@{{self.host}}"] + base_cmd

        if self.dry_run:
            return {{
                "command": " ".join(ssh_cmd),
                "stdout": "(dry-run) pgBackRest not executed",
                "stderr": "",
                "returncode": 0
            }}

        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True
        )

        return {{
            "command": " ".join(ssh_cmd),
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }}
"""
