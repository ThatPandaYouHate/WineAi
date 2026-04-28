"""Application settings loaded from environment / .env file."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    assortments_dir: Path = Field(default=BACKEND_ROOT.parent / "assortments")

    max_wines_to_llm: int = Field(default=80, ge=1, le=1000)

    # Stored as a comma-separated string; exposed as a list via cors_origins.
    cors_origins_raw: str = Field(
        default="http://localhost:5173",
        alias="cors_origins",
    )

    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 5000

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins_raw.split(",")
            if origin.strip()
        ]

    @field_validator("assortments_dir", mode="after")
    @classmethod
    def _resolve_assortments_dir(cls, value: Path) -> Path:
        path = value if value.is_absolute() else (BACKEND_ROOT / value).resolve()
        return path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
