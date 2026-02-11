import sys
from agency.agents.toolsmith_postgresql import ToolsmithPostgreSQL
from agency.workers.postgresql_worker import PostgreSQLWorker
from agency.db.connection import get_connection

if len(sys.argv) < 2:
    print("Usage: python3 test_pgagent.py \"ma question\"")
    sys.exit(1)

user_question = sys.argv[1]

print("\n=== Question ===")
print(user_question)

# 1. Init toolsmith + worker
toolsmith = ToolsmithPostgreSQL()
conn = get_connection()
worker = PostgreSQLWorker(conn)

# 2. Génération du tool
print("\n=== Toolsmith: génération du tool ===")
tool_info = toolsmith.generate_tool(
    user_request=user_question,
    version="18.1"
)

print("Class:", tool_info["class_name"])
print("Type :", tool_info["tool_type"])
print("Command:", tool_info["command"])

# 3. Instruction pour le worker
instruction = {
    "endpoint": "/postgresql",
    "task": "execute_tool",
    "tool_class": tool_info["class_name"],
    "tool_code": tool_info["code"],
    "payload": {}  # vide par défaut
}

# 4. Exécution
print("\n=== Worker: exécution ===")
result = worker.execute(instruction)
print(result)

# 5. Cleanup transaction si erreur SQL
try:
    conn.commit()
except:
    conn.rollback()

conn.close()

