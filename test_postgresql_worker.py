from agency.workers.postgresql_worker import PostgreSQLWorker
from agency.agents.toolsmith_postgresql import ToolsmithPostgreSQL
from agency.db.connection import get_remote_connection

def main():
    print("\n=== TEST WORKER POSTGRESQL (REMOTE DB) ===")

    conn = get_remote_connection()
    toolsmith = ToolsmithPostgreSQL()

    tool_info = toolsmith.generate_tool_for_view(
        view_name="pg_stat_activity",
        version="17",
        conn=conn
    )

    print("\n--- Tool généré ---")
    print("Class:", tool_info["class_name"])
    print("Columns:", tool_info["columns"])

    instruction = {
        "endpoint": "/sql",
        "task": "execute_tool",
        "tool_class": tool_info["class_name"],
        "tool_code": tool_info["code"],
        "payload": {"limit": 5},
    }

    worker = PostgreSQLWorker(conn)
    result = worker.execute(instruction)

    print("\n--- Résultat du worker ---")
    print(result)

if __name__ == "__main__":
    main()

