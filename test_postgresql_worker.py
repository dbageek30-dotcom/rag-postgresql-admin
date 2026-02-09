from agency.workers.postgresql_worker import PostgreSQLWorker
from agency.agents.toolsmith_postgresql import ToolsmithPostgreSQL
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
    )

def main():
    print("\n=== TEST WORKER POSTGRESQL ===")

    conn = get_connection()
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

