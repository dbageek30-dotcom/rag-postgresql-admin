from agency.decision.decision_layer import DecisionLayer
from agency.decision.tool_orchestrator import ToolOrchestrator

dl = DecisionLayer()
orch = ToolOrchestrator()

query = "peux-tu faire un pgbackrest info"
decision = dl.decide(query)

print("\n=== Décision ===")
print(decision)

print("\n=== Exécution ===")
result = orch.execute(decision)

print(result)

