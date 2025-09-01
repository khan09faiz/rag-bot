from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path
from typing import List, Union

class Settings(BaseSettings):
    # Required
    DATABASE_URL: str
    GEMINI_API_KEY: str
    # Optional with defaults
    SECRET_KEY: str = "dev-secret"
    UPLOADS_DIR: str = "uploads"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_PER_MINUTE: int = 60
    BEARER_TOKEN: str | None = None
    ENABLE_FILE_STORAGE: bool = False
    CACHE_SIZE: int = 200

    # Retrieval params
    TOP_K: int = 50
    TOP_M_CONTEXT: int = 10
    SIMILARITY_THRESHOLD: float = 0.30
    RRF_K: int = 60
    MMR_LAMBDA: float = 0.5
    HYBRID_RETRIEVAL: bool = True
    CHUNK_TOKENS: int = 900
    CHUNK_OVERLAP_PCT: int = 12
    MAX_FILE_SIZE_MB: int = 10
    GEMINI_EMBED_MODEL: str = "text-embedding-004"
    GEMINI_CHAT_MODEL: str = "gemini-1.5-flash"
    EMBED_DIM: int = 768

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = "*"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _parse_origins(cls, v):  # type: ignore
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [o.strip() for o in v.split(',') if o.strip()]
        return v

    class Config:
        # Use absolute path so running from project root works.
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        extra = "allow"
        env_file_encoding = "utf-8"

    @field_validator("GEMINI_EMBED_MODEL", mode="before")
    @classmethod
    def _normalize_embed_model(cls, v):  # type: ignore
        # Accept variants and normalize to 'models/text-embedding-004'
        if not isinstance(v, str):
            return v
        val = v.strip()
        if val.startswith("gemini-text-embedding-"):
            val = val.replace("gemini-", "", 1)
        if not val.startswith("models/"):
            val = f"models/{val}"
        return val

settings = Settings()
