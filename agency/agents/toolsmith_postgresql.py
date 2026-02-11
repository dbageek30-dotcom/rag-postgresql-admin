import os
from agency.templates.tool_template_postgresql import TOOL_TEMPLATE_POSTGRESQL
from agency.rag.rag_query import rag_query
from agency.llm.ollama_client import OllamaClient


class ToolsmithPostgreSQL:
    """
    Toolsmith PostgreSQL :
    - interroge la documentation via RAG
    - extrait une commande SQL ou binaire
    - génère un tool Python strict basé sur un template
    """

    def __init__(self, rag_client=None, llm_client=None):
        self.rag = rag_client or rag_query
        default_model = os.getenv("OLLAMA_MODEL_DEFAULT")
        self.llm = llm_client or OllamaClient(model=default_model)

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------
    def generate_tool(self, user_request: str, version: str = "18.1"):
        """
        Génère un tool PostgreSQL basé sur une commande trouvée dans la doc.
        """

        # 1. Récupérer les passages pertinents via RAG
        rag_result = self.rag(user_request, source="postgresql", version=version)
        raw_text = "\n".join(r["content"] for r in rag_result.get("results", []))

        if not raw_text.strip():
            raise ValueError("Aucune documentation pertinente trouvée.")

        # 2. Extraire une commande SQL ou binaire
        command, tool_type = self._extract_command(raw_text)

        # 3. Générer le nom de classe
        class_name = self._make_class_name(command)

        # 4. Générer le code du tool (Injection sécurisée du command_repr)
        tool_code = TOOL_TEMPLATE_POSTGRESQL.format(
            class_name=class_name,
            tool_type=tool_type,
            command=command,
            command_repr=repr(command) # Ajout indispensable pour le template
        )

        return {
            "class_name": class_name,
            "tool_type": tool_type,
            "command": command,
            "code": tool_code
        }

    # ----------------------------------------------------------------------
    # INTERNAL METHODS
    # ----------------------------------------------------------------------
    def _extract_command(self, text: str):
        """
        Extraction stricte d'une commande SQL ou binaire.
        """
        prompt = f"""
Tu es un extracteur STRICT de commandes PostgreSQL.
À partir du texte suivant, extrait UNE SEULE commande SQL ou binaire.

Règles :
- Si c'est SQL : retourne exactement la commande SQL complète.
- Si c'est binaire : retourne uniquement le nom du binaire (ex: pg_dump).
- Ne modifie rien.
- Ne complète rien.
- Ne crée rien.
- Ne devine rien.
- Retourne uniquement la commande, rien d'autre.

Texte :
{text}

Réponds au format strict :
TYPE=<sql|binary>
COMMAND=<commande>
"""

        llm_output = self.llm.chat(
            system_prompt="Extraction stricte de commandes PostgreSQL.",
            user_prompt=prompt
        )

        tool_type = None
        command = None

        for line in llm_output.splitlines():
            if line.startswith("TYPE="):
                tool_type = line.replace("TYPE=", "").strip().lower()
            if line.startswith("COMMAND="):
                command = line.replace("COMMAND=", "").strip()

        if not tool_type or not command:
            raise ValueError(f"Impossible d'extraire une commande valide de l'output : {llm_output}")

        return command, tool_type

    def _make_class_name(self, command: str):
        """
        Génère un nom de classe propre basé sur la commande.
        """
        base = command.split()[0].replace(";", "")
        # Nettoyage supplémentaire pour les binaires (retrait des chemins si présents)
        base = os.path.basename(base)
        return base.title().replace("_", "").replace("-", "") + "Tool"
