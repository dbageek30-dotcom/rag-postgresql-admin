from api.agents.toolsmith_agent import ToolsmithAgent
from api.db import get_connection

def main():
    conn = get_connection()
    agent = ToolsmithAgent()

    # 1. Génération du tool dynamique
    result = agent.generate_tool_for_view(
        view_name="pg_stat_replication",
        version="17",
        conn=conn
    )

    print("\n=== Colonnes retenues ===")
    print(result["columns"])

    print("\n=== Code généré ===")
    print(result["code"])

    # 2. Exécution du code généré
    namespace = {}
    exec(result["code"], namespace)

    ToolClass = namespace[result["class_name"]]
    tool = ToolClass(conn)

    print("\n=== Résultats du tool généré ===")
    rows = tool.run(limit=5)
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()

