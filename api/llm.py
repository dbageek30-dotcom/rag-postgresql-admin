import requests
import json

OLLAMA_URL = "http://10.214.0.8:11434/api/generate"

def llm_query(prompt: str, model: str = "qwen2.5:7b-instruct-q4_K_M"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    data = response.json()
    return data["response"]

