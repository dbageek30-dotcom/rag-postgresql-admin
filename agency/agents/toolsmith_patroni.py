# agency/agents/toolsmith_patroni.py
from agency.templates.tool_template_patroni import TOOL_TEMPLATE_PATRONI

class ToolsmithPatroni:
    def generate_tool_for_command(self, payload: str, arguments: dict = None):
        """
        Découpe le payload pour séparer la commande principale des arguments CLI.
        """
        # Nettoyage et découpage en liste de mots
        parts = payload.strip().split()
        
        if not parts:
            return {"error": "No command provided"}

        # La commande principale est toujours le premier mot (ex: 'list', 'switchover')
        main_command = parts[0]
        
        # Initialisation des options
        options = arguments or {}

        # Parsing manuel des flags CLI (ex: --leader pg_data_1)
        i = 1
        while i < len(parts):
            part = parts[i]
            if part.startswith('--'):
                # Nettoyage de la clé pour Python (ex: --leader -> leader)
                key = part.lstrip('-').replace('-', '_')
                
                # Vérifie si le mot suivant est une valeur ou un autre flag
                if i + 1 < len(parts) and not parts[i+1].startswith('--'):
                    options[key] = parts[i+1]
                    i += 2
                else:
                    # C'est un flag booléen (ex: --force)
                    options[key] = True
                    i += 1
            else:
                # Argument positionnel (souvent ignoré par patronictl en dehors de la commande)
                i += 1

        # Injection dans le template
        # On passe PatroniTool comme class_name par convention
        code = TOOL_TEMPLATE_PATRONI.format(
            class_name="PatroniTool",
            command=main_command
        )

        return {
            "class_name": "PatroniTool",
            "code": code,
            "options": options
        }
