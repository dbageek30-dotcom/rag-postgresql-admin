import requests
import json

OLLAMA_URL = "http://10.214.0.8:11434/api/generate"
MODEL = "qwen2.5:7b-instruct-q4_K_M"


def llm_query(prompt: str) -> str:
    """
    Envoie un prompt à Ollama en mode streaming et reconstruit la réponse complète.
    """
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300)
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

