from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    APP_DATABASE_URL: str = "sqlite:///./data/notas.db"

    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "notas"

    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.65

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()