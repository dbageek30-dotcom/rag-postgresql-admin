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

    def _extract_options_from_doc(self, command_name: str, version: str):
        """
        Utilise RAG + LLM pour extraire les options CLI d'une commande pgBackRest.
        Retourne une liste de noms d'options (sans --).
        """
        question = (
            f"In the pgBackRest documentation (version {version}), "
            f"list all CLI options for the command '{command_name}'. "
            f"Output only the option names, one per line, without descriptions."
        )

        rag_result = self.rag(question, source="pgbackrest", version=version)
        raw_text = "\n".join(r["content"] for r in rag_result.get("results", []))

        if not raw_text.strip():
            return []

        prompt = f"""
You are an expert in pgBackRest.

From the following documentation extract ONLY the CLI option names
for the command '{command_name}'.

Output:
- one option per line
- without descriptions
- without leading '--'
- no extra text.

Documentation:

{raw_text}
"""

        llm_output = self.llm.generate(prompt)

        options = []
        for line in llm_output.splitlines():
            line = line.strip()
            if not line:
                continue
            line = line.lstrip("-")
            if line:
                options.append(line)
        return sorted(set(options))

    def generate_tool_for_command(self, command_name: str, version: str = "2.58.0"):
        """
        Génère un tool dynamique pour une commande pgBackRest.
        """
        options = self._extract_options_from_doc(command_name, version)

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

