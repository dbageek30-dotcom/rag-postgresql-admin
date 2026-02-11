# agency/decision/llm_manager.py

import os
import json
from agency.llm.ollama_client import OllamaClient


class LLMManager:
    """
    LLM Manager (modèle 32B) :
    - reçoit une requête utilisateur brute
    - décide si c'est :
        * une question documentaire (RAG)
        * une action à exécuter (toolsmith)
    - renvoie une décision structurée
    """

    def __init__(self, model: str = None):
        # Modèle du LLM Manager = modèle 32B défini dans .env
        manager_model = model or os.getenv("OLLAMA_MODEL_MANAGER")

        # Client LLM distant
        self.llm = OllamaClient(model=manager_model)

        self.system_prompt = """
Tu es le LLM Manager d'un orchestrateur DBA.
Ton rôle est de ROUTER les requêtes utilisateur.

Tu ne génères PAS de code.
Tu ne génères PAS de commandes shell.
Tu ne génères PAS de SQL.
Tu ne fais que décider :

1) Question documentaire (type = "doc")
   - questions sur PostgreSQL, Patroni, pgBackRest
   - questions sur la configuration, les concepts, les bonnes pratiques
   → réponse via RAG documentaire

2) Action (type = "action")
   - exécution d'une commande Patroni (switchover, failover, reinit, etc.)
   - exécution d'une commande pgBackRest (backup, restore, info, etc.)
   - exécution d'une commande SQL (SELECT, INSERT, etc.)
   → réponse via Toolsmith + Worker

FORMAT DE SORTIE STRICT (JSON uniquement) :

{
  "type": "doc" | "action",
  "action": "patroni" | "pgbackrest" | "postgresql" | null,
  "payload": "texte brut à passer au toolsmith ou au RAG",
  "arguments": {}
}

Ne mets JAMAIS de texte en dehors du JSON.
Ne commente PAS le JSON.
"""

    def route(self, query: str) -> dict:
        user_prompt = f"""
Analyse cette requête utilisateur et renvoie UNIQUEMENT le JSON demandé :

"{query}"
"""

        raw = self.llm.chat(self.system_prompt, user_prompt)

        try:
            data = json.loads(raw)
        except Exception:
            data = {
                "type": "doc",
                "action": None,
                "payload": query,
                "arguments": {}
            }

        if data.get("type") not in ["doc", "action"]:
            data["type"] = "doc"
            data["action"] = None
            data["arguments"] = data.get("arguments", {})

        return data

