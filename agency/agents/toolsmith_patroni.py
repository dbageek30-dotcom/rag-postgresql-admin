# agency/agents/toolsmith_patroni.py

import os
from agency.templates.tool_template_patroni import TOOL_TEMPLATE_PATRONI
from dotenv import load_dotenv
load_dotenv()


class ToolsmithPatroni:
    """
    Toolsmith Patroni :
    - génère une commande Patroni complète
    - ne fait pas appel au LLM
    - produit un tool Python déterministe basé sur un template
    """

    def __init__(self):
        pass

    def generate_tool(self, intent: str, context: dict):
        """
        Génère un tool Patroni basé sur une intention structurée.
        """

        patroni_bin = os.getenv("PATRONI_BIN")
        config_file = os.getenv("PATRONI_CONFIG")

        if not patroni_bin or not config_file:
            raise ValueError("Variables d'environnement PATRONI_BIN ou PATRONI_CONFIG manquantes.")

        # ---------------------------------------------------------
        # 1. Modifier un paramètre PostgreSQL via Patroni
        # ---------------------------------------------------------
        if intent == "modifier un paramètre postgresql":
            param = context["parameter"]
            value = context["value"]

            command = (
                f"{patroni_bin} -c {config_file} edit-config "
                f"--force "
                f"--set postgresql.parameters.{param}={value}"
            )

            class_name = f"PatroniSet{param.title().replace('_','')}Tool"

        # ---------------------------------------------------------
        # 2. Restart Patroni
        # ---------------------------------------------------------
        elif intent == "restart patroni":
            command = (
                f"{patroni_bin} -c {config_file} restart --force"
            )
            class_name = "PatroniRestartTool"

        else:
            raise ValueError(f"Intent Patroni non supporté : {intent}")

        # ---------------------------------------------------------
        # Génération du code Python déterministe
        # ---------------------------------------------------------
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

