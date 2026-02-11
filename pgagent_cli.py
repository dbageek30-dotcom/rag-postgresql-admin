import sys
from agency.rag.rag_query import rag_query
from agency.llm.ollama_client import OllamaClient
from agency.agents.toolsmith_postgresql import ToolsmithPostgreSQL
from agency.workers.postgresql_worker import PostgreSQLWorker
from agency.db.connection import get_connection

def is_action(text):
    action_verbs = [
        "create", "drop", "alter", "grant", "revoke",
        "vacuum", "analyze", "checkpoint",
        "dump", "backup", "restore",
        "start", "stop", "restart"
    ]
    first = text.lower().split()[0]
    return first in action_verbs

if len(sys.argv) < 2:
    print("Usage: python3 pgagent_cli.py \"your question or action\"")
    sys.exit(1)

user_input = sys.argv[1]

print("\n=== Input ===")
print(user_input)

# INIT
conn = get_connection()
worker = PostgreSQLWorker(conn)
toolsmith = ToolsmithPostgreSQL()
llm = OllamaClient(model="llama3.2:3b")

# DECISION LAYER
if is_action(user_input):
    print("\n=== Mode: ACTION (/postgresql) ===")

    tool_info = toolsmith.generate_tool(
        user_request=user_input,
        version="18.1"
    )

    instruction = {
        "endpoint": "/postgresql",
        "task": "execute_tool",
        "tool_class": tool_info["class_name"],
        "tool_code": tool_info["code"],
        "payload": {}
    }

    result = worker.execute(instruction)
    print("\n=== Result ===")
    print(result)

else:
    print("\n=== Mode: INFORMATION (RAG + LLM) ===")

    rag = rag_query(user_input, source="postgresql", version="18.1")
    context = "\n".join([r["content"] for r in rag["results"]])

    answer = llm.chat(
        system_prompt="You are a PostgreSQL expert.",
        user_prompt=f"Question: {user_input}\n\nContext:\n{context}\n\nAnswer clearly."
    )

    print("\n=== Answer ===")
    print(answer)

conn.close()

