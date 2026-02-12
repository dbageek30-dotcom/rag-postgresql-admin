import os
from agency.rag.rag_query import rag_query
from agency.llm.ollama_client import OllamaClient
from agency.templates.tool_template_postgresql_sql import TOOL_TEMPLATE_POSTGRESQL_SQL
from agency.templates.tool_template_postgresql_binary import TOOL_TEMPLATE_POSTGRESQL_BINARY


class ToolsmithPostgreSQL:
    """
    Nouveau Toolsmith PostgreSQL :
    - utilise le RAG pour récupérer la bonne documentation (source=postgresql, version dynamique)
    - génère une commande SQL ou binaire STRICTE basée sur la doc
    - génère un tool Python déterministe basé sur un template
    """

    def __init__(self, rag_client=None, llm_client=None):
        self.rag = rag_client or rag_query
        default_model = os.getenv("OLLAMA_MODEL_DEFAULT")
        self.llm = llm_client or OllamaClient(model=default_model)

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------
    def generate_tool(self, intent: str, context: dict, task_type: str, version: str):
        """
        Génère un tool PostgreSQL basé sur une commande construite à partir de la doc.
        intent : intention utilisateur ("créer un slot logique", "voir les connexions", etc.)
        context : paramètres utiles (dbname, slot_name, plugin, etc.)
        task_type : "sql" ou "binary"
        version : version PostgreSQL ("18.1")
        """

        # 1. Récupération de la doc pertinente via RAG
        rag_result = self.rag(
            query=intent,
            source="postgresql",
            version=version
        )

        raw_text = "\n".join(r["content"] for r in rag_result.get("results", []))
        if not raw_text.strip():
            raise ValueError("Aucune documentation pertinente trouvée pour cette version.")

        # 2. Génération contrôlée de la commande
        command, class_name = self._generate_command(intent, context, task_type, raw_text)

        # 3. Génération du code Python déterministe
        if task_type == "sql":
            tool_code = TOOL_TEMPLATE_POSTGRESQL_SQL.format(
                class_name=class_name,
                command_repr=repr(command)
            )
        else:
            tool_code = TOOL_TEMPLATE_POSTGRESQL_BINARY.format(
                class_name=class_name,
                command_repr=repr(command)
            )

        return {
            "tool_type": task_type,
            "tool_class": class_name,
            "tool_code": tool_code,
            "command": command
        }

    # ----------------------------------------------------------------------
    # INTERNAL METHODS
    # ----------------------------------------------------------------------
    def _generate_command(self, intent: str, context: dict, task_type: str, rag_text: str):
        """
        Génère une commande SQL ou binaire basée STRICTEMENT sur la documentation fournie.
        """

        prompt = f"""
Tu génères UNE commande PostgreSQL STRICTE.

Contexte :
- Intention : {intent}
- Paramètres : {context}
- Type : {task_type}

Documentation autorisée :
{rag_text}

Règles :
- Tu utilises UNIQUEMENT les informations présentes dans la documentation ci-dessus.
- Tu n'inventes aucune fonctionnalité non documentée.
- Tu peux combiner plusieurs éléments documentés pour construire la commande.
- Tu adaptes la commande au contexte fourni.
- Tu renvoies une commande complète, prête à exécuter.
- Format strict :

TYPE=<sql|binary>
COMMAND=<commande>
CLASS_NAME=<NomDeClassePython>
"""

        llm_output = self.llm.chat(
            system_prompt="Génération contrôlée de commandes PostgreSQL basées sur documentation.",
            user_prompt=prompt
        )

        tool_type = None
        command = None
        class_name = None

        for line in llm_output.splitlines():
            if line.startswith("TYPE="):
                tool_type = line.replace("TYPE=", "").strip().lower()
            if line.startswith("COMMAND="):
                command = line.replace("COMMAND=", "").strip()
            if line.startswith("CLASS_NAME="):
                class_name = line.replace("CLASS_NAME=", "").strip()

        if not tool_type or not command or not class_name:
            raise ValueError(f"Impossible d'extraire une commande valide : {llm_output}")

        return command, class_name

