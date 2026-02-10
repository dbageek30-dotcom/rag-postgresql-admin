#!/usr/bin/env python3
import sys, os
import json

# Ajoute la racine du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Pré-warm du singleton pour éviter "Loading weights..."
from agency.llm.embedding_singleton import EmbeddingSingleton
EmbeddingSingleton.get_model()

from agency.decision.decision_layer import DecisionLayer
from agency.decision.tool_orchestrator import ToolOrchestrator

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 manager.py \"votre question\"")
        return

    question = sys.argv[1]

    # 1. Decision Layer
    dl = DecisionLayer()
    decision = dl.decide(question)

    # 2. Orchestrateur
    orchestrator = ToolOrchestrator()
    result = orchestrator.execute(decision)

    # 3. Affichage
    print("\n=== DECISION LAYER ===")
    print(json.dumps(decision, indent=2, ensure_ascii=False))

    print("\n=== RESULTAT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

