from agency.workers.pgbackrest_worker import PgBackRestWorker

# Tool de test (généré à la main)
TEST_TOOL = """
class PgBackRestInfoTest:
    def __init__(self, ssh_host, ssh_user, ssh_key, pgbackrest_bin):
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.pgbackrest_bin = pgbackrest_bin

    def run(self):
        import subprocess

        cmd = [
            "ssh",
            "-i", self.ssh_key,
            f"{self.ssh_user}@{self.ssh_host}",
            f"{self.pgbackrest_bin} info"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
"""

def main():
    print("=== TEST WORKER PGBACKREST (REMOTE) ===")

    worker = PgBackRestWorker()

    tool_params = {
        "ssh_host": "10.210.0.2",
        "ssh_user": "postgres",
        "ssh_key": "/var/lib/postgresql/.ssh/id_rsa",
        "pgbackrest_bin": "/usr/bin/pgbackrest"
    }

    result = worker.execute_tool(TEST_TOOL, tool_params)

    print("\n--- Résultat du worker ---")
    print(result)


if __name__ == "__main__":
    main()

