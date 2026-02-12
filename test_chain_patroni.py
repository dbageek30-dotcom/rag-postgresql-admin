import os
from agency.agents.toolsmith_patroni import ToolsmithPatroni
from agency.workers.patroni_worker import PatroniWorker


def test_chain_patroni():
    print("=== TEST CHAIN: dbamanager → toolsmith_patroni → worker_patroni → Patroni ===")

    # ---------------------------------------------------------
    # 1. Instruction simulée du dbamanager
    # ---------------------------------------------------------
    instruction = {
        "intent": "modifier un paramètre postgresql",
        "context": {
            "parameter": "wal_level",
            "value": "logical"
        }
    }

    print("\n[1] Instruction envoyée au Toolsmith Patroni :")
    print(instruction)

    # ---------------------------------------------------------
    # 2. Appel du Toolsmith Patroni
    # ---------------------------------------------------------
    toolsmith = ToolsmithPatroni()

    toolsmith_output = toolsmith.generate_tool(
        intent=instruction["intent"],
        context=instruction["context"]
    )

    print("\n[2] Toolsmith Patroni a généré :")
    print("Tool class :", toolsmith_output["tool_class"])
    print("Command    :", toolsmith_output["command"])

    # ---------------------------------------------------------
    # 3. Préparer l’instruction pour le worker Patroni
    # ---------------------------------------------------------
    worker_instruction = {
        "endpoint": "/patroni",
        "tool_type": toolsmith_output["tool_type"],
        "tool_class": toolsmith_output["tool_class"],
        "tool_code": toolsmith_output["tool_code"],
        "payload": {
            "ssh_host": os.getenv("PATRONI_LEADER_HOST"),
            "ssh_user": os.getenv("PATRONI_LEADER_USER"),
            "ssh_key": os.getenv("PATRONI_LEADER_SSH_KEY")

        }
    }

    print("\n[3] Instruction envoyée au Worker Patroni :")
    print(worker_instruction)

    # ---------------------------------------------------------
    # 4. Exécution via le Worker Patroni
    # ---------------------------------------------------------
    worker = PatroniWorker()

    print("\n[4] Exécution du tool Patroni sur la VM distante...")
    result = worker.execute(worker_instruction)

    print("\n=== RESULTAT FINAL ===")
    print(result)


if __name__ == "__main__":
    test_chain_patroni()

