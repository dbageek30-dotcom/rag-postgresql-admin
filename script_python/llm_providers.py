import os
import requests

# =========================
#  OLLAMA
# =========================
def call_ollama(question, context, model, url):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": (
                "You are a PostgreSQL administration assistant. "
                "Answer ONLY using the documentation context provided. "
                "If the answer is not in the context, say exactly: "
                "\"The documentation does not contain this information.\""
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        "stream": False
    }

    try:
        resp = requests.post(url, json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content") or data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM ERROR] Ollama: {e}"


# =========================
#  OPENAI (officiel ou compatible)
# =========================
def call_openai(question, context, model, api_key, base_url=None):
    url = base_url or "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": (
                "You are a PostgreSQL administration assistant. "
                "Answer ONLY using the documentation context provided. "
                "If the answer is not in the context, say exactly: "
                "\"The documentation does not contain this information.\""
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM ERROR] OpenAI: {e}"


# =========================
#  HUGGINGFACE INFERENCE API
# =========================
def call_huggingface(question, context, model, api_key):
    url = f"https://api-inference.huggingface.co/models/{model}"

    headers = {"Authorization": f"Bearer {api_key}"}

    payload = {
        "inputs": (
            "You are a PostgreSQL administration assistant.\n"
            "Answer ONLY using the documentation context provided.\n"
            "If the answer is not in the context, say exactly:\n"
            "\"The documentation does not contain this information.\"\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        )
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return str(data)
    except Exception as e:
        return f"[LLM ERROR] HuggingFace: {e}"


# =========================
#  GOOGLE GEMINI
# =========================
def call_gemini(question, context, model, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    "You are a PostgreSQL administration assistant. "
                    "Answer ONLY using the documentation context provided. "
                    "If the answer is not in the context, say exactly: "
                    "\"The documentation does not contain this information.\"\n\n"
                    f"Context:\n{context}\n\nQuestion: {question}"
                )
            }]
        }]
    }

    try:
        resp = requests.post(url, json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"[LLM ERROR] Gemini: {e}"


# =========================
#  MODE SANS LLM
# =========================
def call_none(question, context):
    return None


# =========================
#  ROUTEUR DYNAMIQUE
# =========================
def call_llm(provider, question, context, config):
    provider = provider.lower()

    if provider == "ollama":
        return call_ollama(question, context, config["model"], config["url"])

    if provider == "openai":
        return call_openai(
            question, context,
            config["model"],
            config["api_key"],
            config.get("base_url")
        )

    if provider == "huggingface":
        return call_huggingface(
            question, context,
            config["model"],
            config["api_key"]
        )

    if provider == "gemini":
        return call_gemini(
            question, context,
            config["model"],
            config["api_key"]
        )

    return call_none(question, context)

