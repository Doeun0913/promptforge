from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "PromptForge"
    debug: bool = False

    # LLM API keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Default target model
    default_model: str = "gpt-4o-mini"

    # Pipeline defaults
    default_compression_level: str = "balanced"  # minimal | balanced | aggressive
    confidence_gate_mode: str = "auto"  # auto | semi | manual
    confidence_auto_threshold: float = 0.95
    confidence_semi_lower: float = 0.70
    confidence_semi_upper: float = 0.95

    # Database
    database_url: str = "sqlite+aiosqlite:///./promptforge.db"

    # Cache
    semantic_cache_ttl_seconds: int = 3600
    semantic_cache_similarity_threshold: float = 0.92

    model_config = {"env_prefix": "PF_", "env_file": ".env"}
