# agency/executors/ssh_executor.py

import paramiko
import traceback

class SSHExecutor:
    """
    Exécuteur SSH simple :
    - se connecte via clé privée
    - exécute une commande
    - renvoie stdout, stderr, exit_code
    """

    def __init__(self, host: str, user: str, ssh_key: str):
        self.host = host
        self.user = user
        self.ssh_key = ssh_key

    def run(self, command: str) -> dict:
        try:
            key = paramiko.RSAKey.from_private_key_file(self.ssh_key)

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.host,
                username=self.user,
                pkey=key,
                timeout=30
            )

            stdin, stdout, stderr = client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()

            result = {
                "command": command,
                "exit_code": exit_code,
                "stdout": stdout.read().decode("utf-8"),
                "stderr": stderr.read().decode("utf-8")
            }

            client.close()
            return result

        except Exception as e:
            return {
                "error": str(e),
                "traceback": traceback.format_exc()
            }

