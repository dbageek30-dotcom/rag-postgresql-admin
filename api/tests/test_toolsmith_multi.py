from api.agents.toolsmith_agent import ToolsmithAgent
from api.db import get_connection

# Liste des vues à tester
VIEWS_TO_TEST = [
    "pg_stat_activity",
    "pg_stat_replication",
    "pg_locks",
    "pg_stat_bgwriter",
]

def main():
    conn = get_connection()
    agent = ToolsmithAgent()

    for view in VIEWS_TO_TEST:
        print("\n" + "="*80)
        print(f"=== Génération du tool pour {view} ===")

        # Génération du tool dynamique
        result = agent.generate_tool_for_view(
            view_name=view,
            version="17",
            conn=conn
        )

        print("\nColonnes retenues :")
        print(result["columns"])

        print("\nCode généré :")
        print(result["code"])

        # Exécution du code généré
        namespace = {}
        exec(result["code"], namespace)

        ToolClass = namespace[result["class_name"]]
        tool = ToolClass(conn)

        print("\nRésultats du tool généré :")
        rows = tool.run(limit=5)
        for row in rows:
            print(row)

if __name__ == "__main__":
    main()

