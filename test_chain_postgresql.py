import os
from agency.agents.toolsmith_postgresql import ToolsmithPostgreSQL
from agency.workers.postgresql_worker import PostgreSQLWorker
from agency.db.connection import get_remote_connection


def test_chain():
    print("=== TEST CHAIN: dbamanager → toolsmith → worker → remote PostgreSQL ===")

    # ---------------------------------------------------------
    # 1. Simuler une instruction du dbamanager
    # ---------------------------------------------------------
    instruction = {
        "intent": "créer un slot de réplication logique",
        "task_type": "sql",
        "version": "18.1",
        "context": {
            "slot_name": "slot_test_chain",
            "plugin": "pgoutput",
            "dbname": "postgres"
        }
    }

    print("\n[1] Instruction envoyée au Toolsmith :")
    print(instruction)

    # ---------------------------------------------------------
    # 2. Appeler le Toolsmith PostgreSQL
    # ---------------------------------------------------------
    toolsmith = ToolsmithPostgreSQL()

    toolsmith_output = toolsmith.generate_tool(
        intent=instruction["intent"],
        context=instruction["context"],
        task_type=instruction["task_type"],
        version=instruction["version"]
    )

    print("\n[2] Toolsmith a généré :")
    print(toolsmith_output["tool_class"])
    print(toolsmith_output["command"])

    # ---------------------------------------------------------
    # 3. Préparer l’instruction pour le worker
    # ---------------------------------------------------------
    worker_instruction = {
        "endpoint": "/postgresql",
        "tool_type": toolsmith_output["tool_type"],
        "tool_class": toolsmith_output["tool_class"],
        "tool_code": toolsmith_output["tool_code"],
        "payload": {}  # rien à passer pour SQL
    }

    print("\n[3] Instruction envoyée au Worker :")
    print(worker_instruction)

    # ---------------------------------------------------------
    # 4. Connexion distante + exécution du worker
    # ---------------------------------------------------------
    print("\n[4] Connexion à la base distante...")
    conn = get_remote_connection()

    worker = PostgreSQLWorker(conn)

    print("\n[5] Exécution du tool sur la VM distante...")
    result = worker.execute(worker_instruction)

    print("\n=== RESULTAT FINAL ===")
    print(result)


if __name__ == "__main__":
    test_chain()

