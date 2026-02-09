from agency.decision.decision_layer import DecisionLayer

def run_test(query):
    dl = DecisionLayer()
    result = dl.decide(query)
    print(f"\nQuery: {query}")
    print("Decision:", result)

def main():
    print("\n=== TEST DECISION LAYER STRICT ===")

    # 1. Test SQL
    run_test("/sql SELECT * FROM pg_stat_activity LIMIT 5")

    # 2. Test pgBackRest
    run_test("/tool info")

    # 3. Test Patroni
    run_test("/patroni failover")

    # 4. Test documentation
    run_test("/doc how does WAL archiving work")

    # 5. Test fallback RAG (aucun endpoint)
    run_test("explain wal")

    # 6. Test fallback RAG (question humaine)
    run_test("comment fonctionne le checkpoint")

if __name__ == "__main__":
    main()

