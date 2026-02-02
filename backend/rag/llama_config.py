import os

_settings = None

def get_llama_settings():
    """I.2 - Lazy Initialization & Single Source of Truth."""
    global _settings
    
    if os.environ.get("SYSTEM_BOOTSTRAPPED") != "true":
        raise RuntimeError("Infrastructure accessed before bootstrap_system(). Call bootstrap_system() first.")

    if _settings is None:
        # I.1 - Đảm bảo load các thành phần nặng chỉ khi hàm này được gọi
        from llama_index.core import Settings
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.llms.ollama import Ollama

        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.llm = Ollama(model="llama3", request_timeout=360.0)
        _settings = Settings
        
    return _settings