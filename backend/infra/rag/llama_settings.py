from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from backend.rag.llama_ingest import EMBEDDING_MODEL_TAG

Settings.embed_model = HuggingFaceEmbedding(
    model_name=EMBEDDING_MODEL_TAG
)
