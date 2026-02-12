# agency/agents/toolsmith_patroni.py

import os
from agency.templates.tool_template_patroni import TOOL_TEMPLATE_PATRONI
from dotenv import load_dotenv
load_dotenv()



class ToolsmithPatroni:
    """
    Nouveau Toolsmith Patroni :
    - génère une commande Patroni complète
    - ne fait pas appel au LLM (Patroni est purement CLI)
    - produit un tool Python déterministe basé sur un template
    """

    def __init__(self):
        pass

    def generate_tool(self, intent: str, context: dict):
        """
        Génère un tool Patroni basé sur une intention structurée.
        Exemple d'intention :
            intent = "modifier un paramètre postgresql"
            context = {
                "parameter": "wal_level",
                "value": "logical"
            }
        """

        # ---------------------------------------------------------
        # 1. Construire la commande Patroni
        # ---------------------------------------------------------

        patroni_bin = os.getenv("PATRONI_BIN")
        config_file = os.getenv("PATRONI_CONFIG")
        leader_host = os.getenv("PATRONI_LEADER_HOST")
        leader_user = os.getenv("PATRONI_LEADER_USER")
        leader_key  = os.getenv("PATRONI_LEADER_SSH_KEY")


        if not patroni_bin or not config_file:
            raise ValueError("Variables d'environnement PATRONI_BIN ou PATRONI_CONFIG manquantes.")

        # Exemple : patronictl -c /etc/patroni/patroni.yml edit-config --set postgresql.parameters.wal_level=logical
        if intent == "modifier un paramètre postgresql":
            param = context["parameter"]
            value = context["value"]

            command = (
                f"{patroni_bin} -c {config_file} edit-config "
                f"--force "
                f"--set postgresql.parameters.{param}={value}"
            )

            class_name = f"PatroniSet{param.title().replace('_','')}Tool"

        else:
            raise ValueError(f"Intent Patroni non supporté : {intent}")

        # ---------------------------------------------------------
        # 2. Générer le code Python déterministe
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

