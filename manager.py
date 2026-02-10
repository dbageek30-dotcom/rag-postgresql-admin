#!/usr/bin/env python3
import json
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from agency.decision.decision_layer import DecisionLayer
from agency.orchestrator.tool_orchestrator import ToolOrchestrator

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 manager.py \"votre question\"")
        return

    question = sys.argv[1]

    # 1. Décision Layer
    dl = DecisionLayer()
    decision = dl.route(question)

    # 2. Orchestrateur
    orchestrator = ToolOrchestrator()
    result = orchestrator.execute(decision, question)

    # 3. Affichage propre
    print("\n=== DECISION LAYER ===")
    print(json.dumps(decision, indent=2, ensure_ascii=False))

    print("\n=== RESULTAT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

