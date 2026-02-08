"""Dhakira configuration — loaded from .env file."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API keys
    anthropic_api_key: str = ""

    # Database
    database_url: str = "sqlite:///./data/dhakira.db"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "dhakira_heritage"

    # File storage
    upload_dir: str = "./data"
    audio_dir: str = "./data/audio"
    documents_dir: str = "./data/documents"
    processed_dir: str = "./data/processed"

    # Whisper
    whisper_model: str = "small"

    # Embeddings
    embedding_model: str = "intfloat/multilingual-e5-large"

    # RAG
    claude_model: str = "claude-sonnet-4-5-20250929"
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 200
    rag_top_k: int = 5

    # App
    log_level: str = "info"
    app_title: str = "Dhakira - Qatar Heritage AI Assistant"
    app_version: str = "0.1.0"

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent


settings = Settings()
