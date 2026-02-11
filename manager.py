#!/usr/bin/env python3
import sys, os
import json

# Ajoute la racine du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Pré-warm du singleton pour éviter "Loading weights..."
from agency.llm.embedding_singleton import EmbeddingSingleton
EmbeddingSingleton.get_model()

# On utilise le vrai cerveau du système
from agency.decision.manager import DBAManager


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 manager.py \"votre question\"")
        return

    query = sys.argv[1]

    manager = DBAManager()
    result = manager.handle(query)

    print("\n=== RESULTAT FINAL ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

