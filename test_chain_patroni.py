from dotenv import load_dotenv
load_dotenv()

import os
from agency.agents.toolsmith_patroni import ToolsmithPatroni
from agency.workers.patroni_worker import PatroniWorker


def test_chain_patroni():
    print("=== TEST CHAIN: dbamanager → toolsmith_patroni → worker_patroni → Patroni ===")

    # ---------------------------------------------------------
    # 1. Instruction : modifier wal_level
    # ---------------------------------------------------------
    instruction_edit = {
        "intent": "modifier un paramètre postgresql",
        "context": {
            "parameter": "wal_level",
            "value": "logical"
        }
    }

    print("\n[1] Instruction envoyée au Toolsmith Patroni :")
    print(instruction_edit)

    toolsmith = ToolsmithPatroni()
    tool_edit = toolsmith.generate_tool(
        intent=instruction_edit["intent"],
        context=instruction_edit["context"]
    )

    print("\n[2] Toolsmith Patroni a généré :")
    print("Tool class :", tool_edit["tool_class"])
    print("Command    :", tool_edit["command"])

    worker_instruction_edit = {
        "endpoint": "/patroni",
        "tool_type": tool_edit["tool_type"],
        "tool_class": tool_edit["tool_class"],
        "tool_code": tool_edit["tool_code"],
        "payload": {
            "ssh_host": os.getenv("PATRONI_LEADER_HOST"),
            "ssh_user": os.getenv("PATRONI_LEADER_USER"),
            "ssh_key": os.getenv("PATRONI_LEADER_SSH_KEY")
        }
    }

    print("\n[3] Instruction envoyée au Worker Patroni :")
    print(worker_instruction_edit)

    worker = PatroniWorker()

    print("\n[4] Exécution du tool Patroni (edit-config)...")
    result_edit = worker.execute(worker_instruction_edit)

    print("\n=== RESULTAT EDIT-CONFIG ===")
    print(result_edit)

    # ---------------------------------------------------------
    # 2. Instruction : restart du leader
    # ---------------------------------------------------------
    print("\n=== REDÉMARRAGE DU LEADER ===")

    instruction_restart = {
        "intent": "restart patroni",
        "context": {}
    }

    tool_restart = toolsmith.generate_tool(
        intent=instruction_restart["intent"],
        context=instruction_restart["context"]
    )

    worker_instruction_restart = {
        "endpoint": "/patroni",
        "tool_type": tool_restart["tool_type"],
        "tool_class": tool_restart["tool_class"],
        "tool_code": tool_restart["tool_code"],
        "payload": {
            "ssh_host": os.getenv("PATRONI_LEADER_HOST"),
            "ssh_user": os.getenv("PATRONI_LEADER_USER"),
            "ssh_key": os.getenv("PATRONI_LEADER_SSH_KEY")
        }
    }

    print("\n[RESTART] Instruction envoyée au Worker Patroni :")
    print(worker_instruction_restart)

    print("\n[RESTART] Exécution du restart Patroni...")
    result_restart = worker.execute(worker_instruction_restart)

    print("\n=== RESULTAT RESTART ===")
    print(result_restart)


if __name__ == "__main__":
    test_chain_patroni()

