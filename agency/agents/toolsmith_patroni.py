# agency/agents/toolsmith_patroni.py

import os
import json
from dotenv import load_dotenv
from agency.templates.tool_template_patroni import TOOL_TEMPLATE_PATRONI
from agency.llm.embedding_singleton import EmbeddingSingleton

load_dotenv()


class ToolsmithPatroni:
    """
    Toolsmith Patroni (version AST/JSON) :
    - reçoit une intention structurée du DBA Manager
    - interroge le RAG pour récupérer la documentation versionnée
    - demande au LLM de produire un AST/JSON Patroni (pas une commande shell)
    - compile cet AST en commande shell déterministe
    - génère un tool Python basé sur un template
    """

    def __init__(self, rag_client, llm_client):
        self.rag = rag_client
        self.llm = llm_client
        self.embedder = EmbeddingSingleton.get_model()

    def generate_tool(self, action: str, context: dict):

        patroni_bin = os.getenv("PATRONI_BIN")
        config_file = os.getenv("PATRONI_CONFIG")

        if not patroni_bin or not config_file:
            raise ValueError("Variables d'environnement PATRONI_BIN ou PATRONI_CONFIG manquantes.")

        version = context.get("version")
        if not version:
            raise ValueError("La version de Patroni doit être fournie dans le context (clé 'version').")

        # ---------------------------------------------------------
        # 1. Construire la requête RAG
        # ---------------------------------------------------------
        query = f"patroni version {version} commande pour action '{action}'"
        embedding = self.embedder.encode(query).tolist()

        # ---------------------------------------------------------
        # 2. Interroger le RAG
        # ---------------------------------------------------------
        docs = self.rag.query(query, embedding)

        # ---------------------------------------------------------
        # 3. Appeler le LLM Toolsmith pour obtenir un AST/JSON
        # ---------------------------------------------------------
        llm_input = {
            "action": action,
            "context": context,
            "docs": docs
        }

        ast_json = self.llm.generate_patroni_ast(llm_input)

        try:
            ast = json.loads(ast_json)
        except Exception:
            raise ValueError("Le LLM n'a pas renvoyé un JSON valide pour l'AST Patroni.")

        # ---------------------------------------------------------
        # 4. Compiler l'AST en commande shell
        # ---------------------------------------------------------
        command = self.compile_patroni(ast, patroni_bin, config_file)

        # ---------------------------------------------------------
        # 5. Générer le tool Python déterministe
        # ---------------------------------------------------------
        class_name = f"Patroni{action.title().replace('_', '')}Tool"

        tool_code = TOOL_TEMPLATE_PATRONI.format(
            class_name=class_name,
            command=repr(command)
        )

        return {
            "tool_type": "binary",
            "tool_class": class_name,
            "tool_code": tool_code,
            "command": command,
            "ast": ast
        }

    # ---------------------------------------------------------
    # Compilateur Patroni (générique, dynamique)
    # ---------------------------------------------------------
    def compile_patroni(self, ast, patroni_bin, config_file):
        cmd = [patroni_bin, "-c", config_file, ast["command"]]

        # Arguments positionnels
        for arg in ast.get("positional_args", []):
            cmd.append(str(arg))

        # Flags dynamiques
        for flag, value in ast.get("flags", {}).items():
            if isinstance(value, bool):
                if value:
                    cmd.append(flag)
            else:
                cmd.extend([flag, str(value)])

        return " ".join(cmd)

