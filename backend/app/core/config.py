"""Application configuration."""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Knowledge Gap Agent"
    debug: bool = False
    api_prefix: str = "/api"

    database_url: str = "sqlite+aiosqlite:///./knowledge_gap.db"

    # LLM Provider
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    llamacpp_model_path: Optional[str] = None
    llamacpp_n_ctx: int = 4096

    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "knowledge_base"

    # CMS Integration
    cms_provider: Optional[str] = None
    cms_api_key: Optional[str] = None

    # Search Analytics
    search_provider: Optional[str] = None
    algolia_app_id: Optional[str] = None
    algolia_api_key: Optional[str] = None

    # Support Integration
    support_provider: Optional[str] = None
    support_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
