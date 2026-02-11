from agency.agents.toolsmith_postgresql import ToolsmithPostgreSQL
from agency.db.connection import get_connection

toolsmith = ToolsmithPostgreSQL()

result = toolsmith.generate_tool(
    user_request="Comment obtenir la version de PostgreSQL ?",
    version="18.1"
)

print("Tool généré :")
print(result["class_name"])
print(result["tool_type"])
print(result["command"])
print(result["code"])

