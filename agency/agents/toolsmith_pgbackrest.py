from agency.templates.tool_template_pgbackrest import TOOL_TEMPLATE_PGBACKREST
from agency.rag.rag_query import rag_query
from agency.llm.ollama_client import OllamaClient


class ToolsmithPgBackRest:
    """
    Toolsmith pgBackRest :
    - interroge la doc via RAG
    - extrait les options d'une commande
    - génère un tool Python exécutable pour cette commande
    """

    def __init__(self, rag_client=None, llm_client=None):
        self.rag = rag_client or rag_query
        self.llm = llm_client or OllamaClient()

    def generate_tool_for_command(self, command_name: str, version: str = "latest"):
        """
        Génère un tool dynamique pour une commande pgBackRest.
        """
        # 1. Récupérer la doc via RAG
        question = (
            f"Explain the pgBackRest command '{command_name}' "
            f"and list all its CLI options. "
            f"Output only the option names, one per line."
        )

        rag_result = self.rag(question, source="pgbackrest", version=version)
        raw_text = "\n".join(r["content"] for r in rag_result["results"])

        if not raw_text.strip():
            options = []
        else:
            # 2. Extraction stricte via LLM (OllamaClient)
            prompt = f"""
Here is documentation text about the pgBackRest command '{command_name}':

{raw_text}

Extract ONLY the option names (without descriptions).
Output one option name per line, no explanation.
"""

            llm_output = self.llm.generate(prompt)

            options = []
            for line in llm_output.splitlines():
                line = line.strip().lstrip("-")
                if line:
                    options.append(line)

        # 3. Génération du code du tool
        class_name = f"PgBackRest{command_name.title().replace('-', '').replace('_', '')}Tool"

        tool_code = TOOL_TEMPLATE_PGBACKREST.format(
            class_name=class_name,
            command=command_name
        )

        return {
            "class_name": class_name,
            "options": options,
            "code": tool_code
        }

