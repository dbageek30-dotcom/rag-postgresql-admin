import requests
import json
import numpy as np

OLLAMA_BASE_URL = "http://10.214.0.8:11434"
LLM_MODEL = "qwen2.5:7b-instruct-q4_K_M"
EMBED_MODEL = "bge-base-en-v1.5"


class OllamaClient:
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

    def embed(self, query: str):
        url = f"{OLLAMA_BASE_URL}/api/embeddings"
        payload = {"model": EMBED_MODEL, "prompt": query}

        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        embedding = data.get("embedding")
        if embedding is None:
            raise ValueError("Embedding non trouvé dans la réponse Ollama")

        return np.array(embedding, dtype=float)


def llm_query(prompt: str) -> str:
    client = OllamaClient()
    return client.generate(prompt)

