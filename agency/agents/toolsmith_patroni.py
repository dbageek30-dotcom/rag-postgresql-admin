# agency/agents/toolsmith_patroni.py

import os
from agency.templates.tool_template_patroni import TOOL_TEMPLATE_PATRONI


class ToolsmithPatroni:
    """
    Toolsmith Patroni :
    - ne fait PAS appel au LLM
    - ne fait PAS appel au RAG
    - parse les commandes Patroni
    - applique les règles de sécurité (--force)
    - génère un tool Python dynamique
    """

    def __init__(self):
        pass  # Pas de LLM ici, Patroni est purement CLI

    def generate_tool_for_command(self, payload: str, arguments: dict = None):
        """
        Découpe le payload pour séparer la commande principale des arguments CLI
        et injecte automatiquement les flags de sécurité pour l'automatisation.
        """

        parts = payload.strip().split()
        if not parts:
            return {"error": "No command provided"}

        # Commande principale : list, switchover, failover, restart, etc.
        main_command = parts[0]

        # Options CLI
        options = arguments or {}

        # Parsing manuel des flags CLI
        i = 1
        while i < len(parts):
            part = parts[i]
            if part.startswith('--'):
                key = part.lstrip('-').replace('-', '_')

                # --key=value
                if '=' in part:
                    k, v = part.lstrip('-').split('=', 1)
                    options[k.replace('-', '_')] = v
                    i += 1
                    continue

                # --key value
                if i + 1 < len(parts) and not parts[i+1].startswith('--'):
                    options[key] = parts[i+1]
                    i += 2
                else:
                    # Flag booléen
                    options[key] = True
                    i += 1
            else:
                i += 1

        # Sécurité : forcer --force sur les commandes critiques
        critical_commands = ['switchover', 'failover', 'restart', 'reinit', 'reload']
        if main_command in critical_commands:
            options['force'] = True

        # Génération du code Python dynamique
        class_name = f"Patroni{main_command.title()}Tool"

        code = TOOL_TEMPLATE_PATRONI.format(
            class_name=class_name,
            command=main_command
        )

        return {
            "class_name": class_name,
            "code": code,
            "options": options
        }

