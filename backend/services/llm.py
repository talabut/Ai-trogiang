# backend/services/llm.py
import os
import requests


# Lấy từ ENV, fallback về localhost nếu chạy local không qua docker
OLLAMA_HOST = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Lưu ý: Ollama API chuẩn là /api/generate
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate" 
MODEL_NAME = "phi3:latest"

def generate_answer(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "top_p": 0.9,
                    "num_ctx": 768,        # ↓ giảm từ 1024
                    "num_predict": 200     # giới hạn output length
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
        print(response.text)
        raise RuntimeError(f"LLM generation failed: {str(e)}")