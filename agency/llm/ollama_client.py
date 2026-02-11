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

