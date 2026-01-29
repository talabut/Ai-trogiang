# FILE: backend/rag/llama_config.py
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# Cấu hình Embedding Model (Dùng chung 1 model duy nhất)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def get_embedding_model():
    return HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)

# Thiết lập Global Settings
Settings.embed_model = get_embedding_model()
Settings.llm = None  # Ingest phase không cần LLM