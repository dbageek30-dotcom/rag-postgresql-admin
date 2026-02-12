# agency/agents/toolsmith_patroni.py

import os
from dotenv import load_dotenv
from agency.templates.tool_template_patroni import TOOL_TEMPLATE_PATRONI
from agency.llm.embedding_singleton import EmbeddingSingleton

load_dotenv()


class ToolsmithPatroni:
    """
    Toolsmith Patroni :
    - reçoit une demande structurée du DBA Manager (action, contexte, version)
    - interroge le RAG Patroni pour récupérer la documentation pertinente
    - utilise le LLM pour extraire et composer la commande Patroni exacte
    - génère un tool Python déterministe basé sur un template
    """

    def __init__(self, rag_client, llm_client):
        self.rag = rag_client
        self.llm = llm_client
        self.embedder = EmbeddingSingleton.get_model()

    def generate_tool(self, action: str, context: dict):

        patroni_bin = os.getenv("PATRONI_BIN")
        config_file = os.getenv("PATRONI_CONFIG")

        if not patroni_bin or not config_file:
            raise ValueError("Variables d'environnement PATRONI_BIN ou PATRONI_CONFIG manquantes.")

        version = context.get("version")
        if not version:
            raise ValueError("La version de Patroni doit être fournie dans le context (clé 'version').")

        # ---------------------------------------------------------
        # 1. Construire la requête RAG
        # ---------------------------------------------------------
        query = f"patroni version {version} commande pour action '{action}'"
        embedding = self.embedder.encode(query).tolist()

        # ---------------------------------------------------------
        # 2. Interroger le RAG correctement
        # ---------------------------------------------------------
        docs = self.rag.query(query, embedding)

        # ---------------------------------------------------------
        # 3. Appeler le LLM Toolsmith (7B)
        # ---------------------------------------------------------
        llm_input = {
            "action": action,
            "context": context,
            "docs": docs,
            "patroni_bin": patroni_bin,
            "config_file": config_file,
        }

        command = self.llm.generate_patroni_command(llm_input)

        if not isinstance(command, str) or not command.strip():
            raise ValueError("Le LLM n'a pas renvoyé de commande Patroni valide.")

        # ---------------------------------------------------------
        # 4. Générer le tool Python déterministe
        # ---------------------------------------------------------
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

