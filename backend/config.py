"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://promptops:promptops@localhost:5432/promptops"
    # Sync URL for Alembic migrations
    DATABASE_URL_SYNC: str = "postgresql://promptops:promptops@localhost:5432/promptops"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    API_KEY_PREFIX: str = "sq-"

    # OpenAI (optional)
    OPENAI_API_KEY: Optional[str] = None

    # Embedding
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Cache
    CACHE_SIMILARITY_THRESHOLD: float = 0.92
    CACHE_TTL_SECONDS: int = 3600

    # Model pricing (per 1K tokens, in USD)
    MODEL_PRICING: dict = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
