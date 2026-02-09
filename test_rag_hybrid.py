from agency.decision.decision_layer import DecisionLayer
from agency.decision.tool_orchestrator import ToolOrchestrator

def test_rag(query: str):
    print("\n==============================")
    print(f"TEST RAG HYBRIDE : {query}")
    print("==============================")

    dl = DecisionLayer()
    orch = ToolOrchestrator()

    # 1. Décision
    decision = dl.decide(query)
    decision["query"] = query  # important pour le RAG

    print("\n--- Décision ---")
    print(decision)

    # 2. Exécution orchestrateur
    result = orch.execute(decision)

    print("\n--- Résultat RAG ---")
    print(result)


if __name__ == "__main__":
    # Test PostgreSQL
    test_rag("comment fonctionne le WAL dans PostgreSQL")

    # Test pgBackRest
    test_rag("explique moi comment fonctionne une stanza pgbackrest")

    # Test Patroni
    test_rag("comment faire un failover avec patroni")

    # Test général
    test_rag("comment fonctionne la réplication")

