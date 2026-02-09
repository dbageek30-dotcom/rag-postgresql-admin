from agency.agents.toolsmith_pgbackrest import ToolsmithPgBackRest

def main():
    agent = ToolsmithPgBackRest()

    # Commandes à tester (backup désactivé pour éviter un backup réel)
    commands_to_test = [
        ("info", {}),
        ("check", {"stanza": "pg_data"}),
        ("stanza-create", {"stanza": "pg_data"}),
        # ("backup", {"stanza": "pg_data", "type": "full"}),  # ⚠️ désactivé volontairement
    ]

    for cmd, args in commands_to_test:
        print("\n" + "="*80)
        print(f"=== Génération du tool pour pgBackRest '{cmd}' ===")

        # 1. Génération du tool
        result = agent.generate_tool_for_command(cmd)

        print("\nOptions détectées :")
        print(result["options"])

        print("\nCode généré :")
        print(result["code"])

        # 2. Compilation du tool
        namespace = {}
        exec(result["code"], namespace)

        ToolClass = namespace[result["class_name"]]

        # 3. Exécution réelle via SSH
        tool = ToolClass(dry_run=False)

        print("\nRésultat du tool généré :")
        output = tool.run(args=args)
        print(output)

if __name__ == "__main__":
    main()

