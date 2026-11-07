"""
config.py

Loads project settings from the .env file.
If the .env file does not exist, default values suitable for testing are used.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./test_dev.db"
    secret_key: str = "dev-only-insecure-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Vector index file paths (relative to the backend directory).
    vector_index_path: str = "../data/processed/vector_index.faiss"
    vector_metadata_path: str = "../data/processed/vector_metadata.json"

    # Embedding model: a locally fine-tuned version is used instead of the public base model.
    # This path is resolved relative to the backend directory where Uvicorn is started.
    embedding_model_name: str = "models_cache/finetuned-embedding-health"

    # Ollama configuration.
    ollama_host: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:8b"

    retrieval_top_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()