from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"
    database_url: str = "sqlite:///./drivemind.db"
    secret_key: str = "change-me-before-deploying"
    token_encryption_key: str | None = None

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"

    ai_provider: str = "dummy"
    embedding_provider: str = "dummy"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    embedding_dim: int = 768
    max_docs_per_index: int = 50

    model_config = ConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
