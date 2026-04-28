from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Neuroimagen Server Biocruces"
    environment: str = "development"
    api_prefix: str = "/api"
    database_url: str = Field(
        default="postgresql+psycopg://neuroimagen:neuroimagen@postgres:5432/neuroimagen"
    )
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    storage_root: Path = Path("/app/data/studies")
    allowed_extensions: str = ".nii,.nii.gz,.dcm,.zip,.tar,.tar.gz,.gz,.json,.txt"
    max_upload_size_mb: int = 1024
    processor_command: str = (
        "python /app/external_processor/dummy_processor.py "
        "--input {input_dir} --output {output_dir} --study-id {study_id}"
    )
    processor_name: str = "dummy-development-processor"
    processor_version: str | None = "0.1.0"
    cors_origins: str = "http://localhost,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_extension_list(self) -> list[str]:
        return [item.strip().lower() for item in self.allowed_extensions.split(",") if item.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
