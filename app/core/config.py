from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Yee-Daa API", alias="APP_NAME")
    project_name: str = Field(default="Yee-Daa API", alias="PROJECT_NAME")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    api_version: str = Field(default="0.1.0", alias="API_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/project_db",
        alias="DATABASE_URL",
    )
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )

    storage_provider: Literal["minio", "s3"] = Field(
        default="minio",
        alias="STORAGE_PROVIDER",
    )
    storage_bucket: str = Field(default="omnicorp", alias="STORAGE_BUCKET")
    storage_region: str = Field(default="us-east-1", alias="STORAGE_REGION")
    storage_access_key: str = Field(default="omnicorp_user", alias="STORAGE_ACCESS_KEY")
    storage_secret_key: str = Field(default="omnicorp_pw", alias="STORAGE_SECRET_KEY")
    storage_endpoint_url: str | None = Field(
        default="http://localhost:9000",
        alias="STORAGE_ENDPOINT_URL",
    )
    storage_public_base_url: str = Field(
        default="http://localhost:9000/omnicorp",
        alias="STORAGE_PUBLIC_BASE_URL",
    )
    storage_max_upload_bytes: int = Field(
        default=10_485_760,
        alias="STORAGE_MAX_UPLOAD_BYTES",
    )
    storage_force_path_style: bool = Field(
        default=True,
        alias="STORAGE_FORCE_PATH_STYLE",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("storage_provider", mode="before")
    @classmethod
    def normalize_storage_provider(cls, value: str) -> str:
        return value.strip().lower() if isinstance(value, str) else value


@lru_cache
def get_settings() -> Settings:
    return Settings()
