from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    API_HOST: str
    API_PORT: int

    JWT_SECRET: str

    OLLAMA_BASE_URL: str

    QDRANT_URL: str
    QDRANT_API_KEY: str = ""

    COLLECTION_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()