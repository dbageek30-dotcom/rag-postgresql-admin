# agency/agents/toolsmith_pgbackrest.py
from agency.templates.tool_template_pgbackrest import TOOL_TEMPLATE_PGBACKREST
from agency.rag.rag_query import rag_query
from agency.llm.ollama_client import OllamaClient

class ToolsmithPgBackRest:
    def __init__(self, rag_client=None, llm_client=None):
        self.rag = rag_client or rag_query
        self.llm = llm_client or OllamaClient()

    def generate_tool_for_command(self, payload: str, version: str = "2.58.0"):
        # 1. Parsing du payload (ex: "info --stanza=demo")
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
                # Gestion de --key=value ou --key value
                key_part = part.lstrip('-').split('=')
                key = key_part[0].replace('-', '_')
                
                if len(key_part) > 1: # format --stanza=demo
                    args_dict[key] = key_part[1]
                    i += 1
                elif i + 1 < len(parts) and not parts[i+1].startswith('--'): # format --stanza demo
                    args_dict[key] = parts[i+1]
                    i += 2
                else: # format booléen --force
                    args_dict[key] = True
                    i += 1
            else:
                i += 1

        # 2. On garde l'extraction d'options via RAG si tu en as besoin pour plus tard
        # (Mais ici on utilise surtout les args_dict extraits du payload utilisateur)
        
        class_name = f"PgBackRest{command_name.title().replace('-', '').replace('_', '')}Tool"

        tool_code = TOOL_TEMPLATE_PGBACKREST.format(
            class_name=class_name,
            command=command_name
        )

        return {
            "class_name": class_name,
            "code": tool_code,
            "options": args_dict
        }
