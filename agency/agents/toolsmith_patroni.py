# agency/agents/toolsmith_patroni.py

import os
from dotenv import load_dotenv
from agency.templates.tool_template_patroni import TOOL_TEMPLATE_PATRONI

load_dotenv()


class ToolsmithPatroni:
    """
    Toolsmith Patroni :
    - reçoit une demande structurée du DBA Manager (action, contexte, version)
    - interroge le RAG Patroni via rag_client
    - utilise le LLM (qwen2.5 7B) pour lire la doc et composer la commande Patroni exacte
    - génère un tool Python déterministe basé sur un template, prêt pour le worker
    """

    def __init__(self, rag_client, llm_client):
        """
        rag_client : client RAG déjà configuré (BM25 + vecteurs, etc.)
        llm_client : client LLM (Ollama qwen2.5:7b-instruct-q4_K_M)
        """
        self.rag = rag_client
        self.llm = llm_client

    def generate_tool(self, action: str, context: dict):
        """
        Génère un tool Patroni basé sur une action structurée.

        Exemple de context :
            {
                "version": "3.3.0",
                "cluster_name": "pgcluster",
                "target": "leader",
                ...
            }
        """

        patroni_bin = os.getenv("PATRONI_BIN")
        config_file = os.getenv("PATRONI_CONFIG")

        if not patroni_bin or not config_file:
            raise ValueError("Variables d'environnement PATRONI_BIN ou PATRONI_CONFIG manquantes.")

        version = context.get("version")
        if not version:
            raise ValueError("La version de Patroni doit être fournie dans le context (clé 'version').")

        # 1. Interroger le RAG Patroni pour cette version + action
        query = f"patroni version {version} commande pour action '{action}'"
        docs = self.rag.query(query)

        # 2. Appel explicite au LLM Toolsmith (7B) pour composer la commande
        llm_input = {
            "action": action,
            "context": context,
            "docs": docs,
            "patroni_bin": patroni_bin,
            "config_file": config_file,
        }

        # 👉 C’est ICI que ton qwen2.5:7b est utilisé
        command = self.llm.generate_patroni_command(llm_input)

        if not isinstance(command, str) or not command.strip():
            raise ValueError("Le LLM n'a pas renvoyé de commande Patroni valide.")

        # 3. Génération du code Python déterministe via le template
        class_name = f"Patroni{action.title().replace('_', '')}Tool"

        tool_code = TOOL_TEMPLATE_PATRONI.format(
            class_name=class_name,
            command=repr(command)
        )

        return {
            "tool_type": "binary",
            "tool_class": class_name,
            "tool_code": tool_code,
            "command": command
        }

