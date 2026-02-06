import os
from google import genai

# Clé API Gemini Studio (format AIza...)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"   # ou "gemini-2.5-flash" si tu l'as activé


def llm_query(prompt: str) -> str:
    """
    Envoie un prompt à Gemini via le SDK officiel google-genai.
    """
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": 0,
            "max_output_tokens": 2048,
        }
    )

    return response.text.strip()

