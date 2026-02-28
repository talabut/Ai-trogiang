# backend/services/llm.py

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"


def generate_answer(prompt: str) -> str:
    """
    Generate answer from Ollama (phi3:mini).
    Strict low-temperature config for RAG grounding.
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,   # 🔥 giảm hallucination
                    "top_p": 0.9
                }
            },
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "").strip()

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Ollama server is not running. Please start with: ollama serve"
        )

    except Exception as e:
        raise RuntimeError(f"LLM generation failed: {str(e)}")