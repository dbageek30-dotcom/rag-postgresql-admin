# agency/executors/ssh_executor.py

import paramiko
import traceback
import os

class SSHExecutor:
    """
    Exécuteur SSH simple :
    - supporte RSA et ED25519 automatiquement
    - se connecte via clé privée
    - exécute une commande
    - renvoie stdout, stderr, exit_code
    """

    def __init__(self, host: str, user: str, ssh_key: str):
        self.host = host
        self.user = user
        self.ssh_key = ssh_key

    def _load_private_key(self):
        """
        Détecte automatiquement le type de clé :
        - RSA
        - ED25519
        """

        with open(self.ssh_key, "r") as f:
            first_line = f.readline().strip()

        if "BEGIN OPENSSH PRIVATE KEY" in first_line:
            # Peut être ED25519 ou autre → on laisse Paramiko détecter
            try:
                return paramiko.Ed25519Key.from_private_key_file(self.ssh_key)
            except Exception:
                pass

        if "BEGIN RSA PRIVATE KEY" in first_line:
            return paramiko.RSAKey.from_private_key_file(self.ssh_key)

        # Fallback : laisser Paramiko deviner
        try:
            return paramiko.Ed25519Key.from_private_key_file(self.ssh_key)
        except Exception:
            return paramiko.RSAKey.from_private_key_file(self.ssh_key)

    def run(self, command: str) -> dict:
        try:
            key = self._load_private_key()

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

