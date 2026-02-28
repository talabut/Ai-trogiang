# backend/services/llm.py
import os
import requests


# Lấy từ ENV, fallback về localhost nếu chạy local không qua docker
OLLAMA_HOST = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Lưu ý: Ollama API chuẩn là /api/generate
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate" 
MODEL_NAME = "phi3:latest"


def generate_answer(prompt: str) -> str:
    """
    Generate answer from Ollama (phi3:latest).
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