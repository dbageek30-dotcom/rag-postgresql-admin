from agency.agents.toolsmith_pgbackrest import ToolsmithPgBackRest
from agency.workers.pgbackrest_worker import PgBackRestWorker


def main():
    print("=== TEST END-TO-END: Toolsmith → Worker → pgBackRest ===")

    # 1. Initialiser le Toolsmith
    toolsmith = ToolsmithPgBackRest()

    # 2. Générer un tool pour la commande "info"
    tool_data = toolsmith.generate_tool_for_command("info", version="2.58.0")

    print("\n--- Tool généré ---")
    print("Class name:", tool_data["class_name"])
    print("Options extraites:", tool_data["options"])
    print("\nCode du tool:\n")
    print(tool_data["code"])

    # 3. Initialiser le Worker
    worker = PgBackRestWorker()

    # 4. Paramètres dynamiques pour la VM distante
    tool_params = {
        "ssh_host": "10.210.0.2",
        "ssh_user": "postgres",
        "ssh_key": "/home/postgres/.ssh/id_rsa",  # adapte si nécessaire
        "pgbackrest_bin": "/usr/bin/pgbackrest",
        # Exemple d’options (si la commande en a)
        # "stanza": "pg_data"
    }

    # 5. Exécuter le tool généré
    print("\n--- Exécution du tool via Worker ---")
    result = worker.execute_tool(tool_data["code"], tool_params)

    print("\n--- Résultat final ---")
    print(result)


if __name__ == "__main__":
    main()

