# agency/agents/toolsmith_pgbackrest.py

import os
from agency.templates.tool_template_pgbackrest import TOOL_TEMPLATE_PGBACKREST
from agency.rag.rag_query import rag_query
from agency.llm.ollama_client import OllamaClient


class ToolsmithPgBackRest:
    def __init__(self, rag_client=None, llm_client=None):
        """
        Toolsmith pour pgBackRest :
        - utilise le RAG pour comprendre la doc
        - utilise un LLM (7B par défaut) pour générer le code
        """

        # RAG local
        self.rag = rag_client or rag_query

        # Modèle par défaut (7B) défini dans .env
        default_model = os.getenv("OLLAMA_MODEL_DEFAULT")

        # Client LLM distant
        self.llm = llm_client or OllamaClient(model=default_model)

    # ----------------------------------------------------------------------
    # Génération d’un tool pgBackRest
    # ----------------------------------------------------------------------
    def generate_tool_for_command(self, payload: str, version: str = "2.58.0"):
        """
        Transforme une commande utilisateur en tool Python dynamique.
        Exemple : "info --stanza=demo"
        """

        # 1. Parsing du payload
        parts = payload.strip().split()
        if not parts:
            return {"error": "No command provided"}

        command_name = parts[0]
        args_dict = {}

        # Parsing des options CLI
        i = 1
        while i < len(parts):
            part = parts[i]
            if part.startswith('--'):
                key_part = part.lstrip('-').split('=')
                key = key_part[0].replace('-', '_')

                if len(key_part) > 1:  # format --stanza=demo
                    args_dict[key] = key_part[1]
                    i += 1
                elif i + 1 < len(parts) and not parts[i+1].startswith('--'):  # format --stanza demo
                    args_dict[key] = parts[i+1]
                    i += 2
                else:  # booléen --force
                    args_dict[key] = True
                    i += 1
            else:
                i += 1

        # 2. Nom de la classe
        class_name = f"PgBackRest{command_name.title().replace('-', '').replace('_', '')}Tool"

        # 3. Génération du code Python dynamique
        tool_code = TOOL_TEMPLATE_PGBACKREST.format(
            class_name=class_name,
            command=command_name
        )

        return {
            "class_name": class_name,
            "code": tool_code,
            "options": args_dict
        }

