from agency.agents.toolsmith_postgresql import ToolsmithPostgreSQL
from agency.workers.postgresql_worker import PostgreSQLWorker
from agency.db.connection import get_connection

toolsmith = ToolsmithPostgreSQL()
conn = get_connection()
worker = PostgreSQLWorker(conn)

# 1. Générer un tool
tool_info = toolsmith.generate_tool(
    user_request="Comment obtenir la version de PostgreSQL ?",
    version="18.1"
)

instruction = {
    "endpoint": "/postgresql",
    "task": "execute_tool",
    "tool_class": tool_info["class_name"],
    "tool_code": tool_info["code"],
    "payload": {}
}

# 2. Exécuter via le worker
result = worker.execute(instruction)
print(result)

# 3. Cleanup
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS distributors;")
conn.commit()
cur.close()

