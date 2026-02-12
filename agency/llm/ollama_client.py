import os
import requests
import json
from dotenv import load_dotenv

# Charger .env
load_dotenv()

from agency.llm.embedding_singleton import EmbeddingSingleton


class OllamaClient:
    """
    Client Ollama générique :
    - modèle configurable via paramètre OU .env
    - host configurable via paramètre OU .env
    - supporte /api/chat
    - embeddings locaux via EmbeddingSingleton
    """

    def __init__(self, model=None, host=None):
        # Valeurs par défaut depuis .env
        self.model = model or os.getenv("OLLAMA_MODEL_DEFAULT")
        self.host = (host or os.getenv("OLLAMA_HOST")).rstrip("/")

        # Embeddings locaux
        self.embedding_model = EmbeddingSingleton.get_model()

    # -----------------------------------------------------
    # 1. Chat LLM (API moderne)
    # -----------------------------------------------------
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.host}/api/chat"

        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

        response = requests.post(url, json=payload, timeout=600)
        response.raise_for_status()

        data = response.json()
        return data["message"]["content"]

    # -----------------------------------------------------
    # 2. Embeddings locaux (PAS via Ollama)
    # -----------------------------------------------------
    def embed(self, query: str):
        vector = self.embedding_model.encode(query)
        return vector.tolist()

    # -----------------------------------------------------
    # 3. Génération d'un AST/JSON Patroni via le LLM Toolsmith
    # -----------------------------------------------------
    def generate_patroni_ast(self, llm_input: dict) -> str:
        """
        Génère un AST/JSON Patroni à partir :
        - de l'action structurée
        - du contexte
        - de la documentation RAG
        """

        system_prompt = (
            "You are a Toolsmith LLM. Your job is to generate a structured AST/JSON describing a Patroni command.\n"
            "You MUST NOT generate shell commands.\n"
            "You MUST NOT generate text outside JSON.\n"
            "You MUST NOT invent flags or arguments that are not present in the documentation provided.\n"
            "\n"
            "Your output MUST be a JSON object with the following structure:\n"
            "{\n"
            "  \"tool\": \"patroni\",\n"
            "  \"command\": \"<command_name>\",\n"
            "  \"positional_args\": [ ... ],\n"
            "  \"flags\": {\n"
            "      \"<flag>\": <value>\n"
            "  }\n"
            "}\n"
            "\n"
            "Rules:\n"
            "- Only output JSON.\n"
            "- No explanations.\n"
            "- No markdown.\n"
            "- No shell syntax.\n"
        )

        user_prompt = f"""
Action request:
{json.dumps(llm_input["context"], indent=2)}

Relevant Patroni documentation:
{llm_input["docs"]}

Generate the AST/JSON for this Patroni command.
"""

        return self.chat(system_prompt, user_prompt)

