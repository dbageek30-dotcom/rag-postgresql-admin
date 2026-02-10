# agency/agents/toolsmith_patroni.py

from agency.templates.tool_template_patroni import TOOL_TEMPLATE_PATRONI

class ToolsmithPatroni:
    """
    Génère dynamiquement un outil Patroni basé sur un template,
    exactement comme pgBackRest.
    Le Worker injecte :
      - ssh_host
      - ssh_user
      - ssh_key
      - patroni_bin
      - config_file
    """

    def generate_tool_for_command(self, command: str, options: dict = None) -> dict:
        """
        command : str
            Exemple : "switchover"
        options : dict
            Exemple : {"leader": "pg_data_1", "candidate": "pg_data_2", "force": True}
        """
        class_name = "PatroniTool"
        options = options or {}

        # On remplit le template avec la commande et le nom de classe
        code = TOOL_TEMPLATE_PATRONI.format(
            class_name=class_name,
            command=command
        )

        return {
            "class_name": class_name,
            "code": code,
            "options": options
        }

