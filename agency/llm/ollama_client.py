import os
import requests
import json
import numpy as np

# Désactiver les logs HF / Transformers AVANT tout import HF
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from agency.llm.embedding_singleton import EmbeddingSingleton

# ---------------------------------------------------------
# Ollama (LLM uniquement)
# ---------------------------------------------------------
OLLAMA_BASE_URL = "http://10.214.0.8:11434"
LLM_MODEL = "qwen2.5:7b-instruct-q4_K_M"


class OllamaClient:
    def __init__(self):
        # Singleton : un seul modèle d'embedding pour toute l'application
        self.embedding_model = EmbeddingSingleton.get_model()

    # -----------------------------------------------------
    # 1. Génération LLM via Ollama
    # -----------------------------------------------------
    def generate(self, prompt: str) -> str:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {"model": LLM_MODEL, "prompt": prompt, "stream": True}

        response = requests.post(url, json=payload, stream=True, timeout=300)
        response.raise_for_status()

        full_text = ""
        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue

            chunk = data.get("response", "")
            full_text += chunk

            if data.get("done"):
                break

        return full_text.strip()

    # -----------------------------------------------------
    # 2. Embeddings locaux (PAS via Ollama)
    # -----------------------------------------------------
    def embed(self, query: str):
        vector = self.embedding_model.encode(query)
        return vector.tolist()


def llm_query(prompt: str) -> str:
    client = OllamaClient()
    return client.generate(prompt)

