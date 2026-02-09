from agency.decision.tool_orchestrator import ToolOrchestrator


def main():
    orch = ToolOrchestrator()

    decision = {
        "action": "tool:pgbackrest",
        "payload": "info",
        "arguments": {}
    }

    result = orch.execute(decision)

    print("\n=== Résultat Orchestrator ===")
    print(result)


if __name__ == "__main__":
    main()

