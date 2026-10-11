from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root, so .env and relative paths work no matter which directory you run from
BASE_DIR = Path(__file__).resolve().parents[2]


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

    CORS_ALLOWED_ORIGINS: str = "*"
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "medibot_docs"

    DATA_DIR: Path = Path("data/mediassist_data")
    # Single source of truth: the chunker's tokenizer and the dense embedder both use this
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384
    SPARSE_MODEL: str = "Qdrant/bm25"
    CHUNK_MAX_TOKENS: int = 480

    @field_validator("DATA_DIR")
    @classmethod
    def resolve_from_project_root(cls, path: Path) -> Path:
        return path if path.is_absolute() else BASE_DIR / path

    @property
    def CORS_ALLOWED_ORIGINS_LIST(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",")]


config = Config()
