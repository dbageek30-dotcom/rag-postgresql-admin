import os
from dotenv import load_dotenv

from agency.agents.toolsmith_pgbackrest import ToolsmithPgBackRest
from agency.agents.toolsmith_agent import ToolsmithAgent  # PostgreSQL
from agency.agents.toolsmith_patroni import ToolsmithPatroni

from agency.workers.pgbackrest_worker import PgBackRestWorker
from agency.workers.postgresql_worker import PostgreSQLWorker
from agency.workers.patroni_worker import PatroniWorker

from agency.rag.rag_hybrid import RAGHybrid
from agency.llm.ollama_client import OllamaClient


class ToolOrchestrator:
    """
    Orchestrateur propre :
    - distingue local vs distant
    - route Toolsmith → Worker
    - compatible avec DecisionLayer strict
    """

    def __init__(self):
        load_dotenv()

        # Paramètres DB locaux
        self.db_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }

        # Paramètres distants (pgBackRest)
        self.remote_params = {
            "ssh_host": os.getenv("REMOTE_HOST"),
            "ssh_user": os.getenv("REMOTE_USER", "postgres"),
            "ssh_key": os.getenv("REMOTE_SSH_KEY"),
            "pgbackrest_bin": os.getenv("PGBACKREST_BIN", "/usr/bin/pgbackrest"),
        }

        # Paramètres Patroni
        self.patroni_params = {
            "patroni_bin": os.getenv("PATRONI_BIN", "/usr/bin/patronictl"),
            "config_file": os.getenv("PATRONI_CONFIG", "/etc/patroni.yml"),
            "ssh_host": os.getenv("REMOTE_HOST"), 
            "ssh_user": os.getenv("REMOTE_USER", "postgres"), 
            "ssh_key": os.getenv("REMOTE_SSH_KEY"),
        }

        # Toolsmiths
        self.toolsmiths = {
            "postgresql": ToolsmithAgent(),
            "pgbackrest": ToolsmithPgBackRest(),
            "patroni": ToolsmithPatroni(),
        }

        # Workers
        self.workers = {
            "postgresql": PostgreSQLWorker(self.db_params),
            "pgbackrest": PgBackRestWorker(),
            "patroni": PatroniWorker(self.patroni_params),
        }

        # LLM instancié UNE SEULE FOIS
        self.llm = OllamaClient()

    def execute(self, decision: dict):
        action = decision.get("action")
        payload = decision.get("payload", "")
        args = decision.get("arguments", {})

        # ------------------------------------------------------------
        # PostgreSQL (local)
        # ------------------------------------------------------------
        if action == "tool:postgresql":
            toolsmith = self.toolsmiths["postgresql"]
            tool_data = toolsmith.generate_tool_for_command(payload)

            namespace = {}
            exec(tool_data["code"], namespace)

            ToolClass = namespace[tool_data["class_name"]]
            tool = ToolClass(**self.db_params)

            return tool.run(args=args)

        # ------------------------------------------------------------
        # pgBackRest (distant)
        # ------------------------------------------------------------
        if action == "tool:pgbackrest":
            toolsmith = self.toolsmiths["pgbackrest"]
            tool_data = toolsmith.generate_tool_for_command(payload)

            worker = self.workers["pgbackrest"]
            return worker.execute_tool(tool_data["code"], self.remote_params)

        # ------------------------------------------------------------
        # Patroni (distant, dynamique via template)
        # ------------------------------------------------------------
        if action == "tool:patroni":
            toolsmith = self.toolsmiths["patroni"]

            # Le Toolsmith génère : class_name, code, options
            tool_data = toolsmith.generate_tool_for_command(payload, args)

            worker = self.workers["patroni"]

            # On passe :
            # - code généré
            # - paramètres SSH + patroni_bin + patroni_config
            # - options dynamiques
            patroni_params = {
                **self.patroni_params,
                "options": tool_data.get("options", {})
            }

            return worker.execute_tool(tool_data["code"], patroni_params)

        # ------------------------------------------------------------
        # RAG documentaire
        # ------------------------------------------------------------
        if action == "rag:doc":
            rag = RAGHybrid(self.db_params)
            query_embedding = self.llm.embed(query=payload)
            return rag.query(payload, query_embedding)

        # ------------------------------------------------------------
        # Fallback
        # ------------------------------------------------------------
        return {"error": "Action inconnue", "action": action}

