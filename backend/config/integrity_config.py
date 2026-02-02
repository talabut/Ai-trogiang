import os
from pydantic_settings import BaseSettings
from typing import List, Set

class Settings(BaseSettings):
    PROJECT_NAME: str = "ai-tro-giang"

    # CORS
    ALLOWED_CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: Set[str] = {".txt", ".pdf", ".docx"}

    # Paths
    DATA_DIR: str = "./data"
    SQLITE_DB_PATH: str = "./data/app_database.db"
    FAISS_INDEX_DIR: str = "./data/faiss_index"

    # RAG
    RETRIEVAL_THRESHOLD: float = 0.6

    # Concurrency & Safety
    MAX_CONCURRENT_INGEST: int = 1
    MAX_MEMORY_MB: int = 2048

    class Config:
        env_file = ".env"

settings = Settings()
