"""Configuration; secrets are deliberately excluded from API responses."""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EKA_", env_file=PROJECT_ROOT / ".env", extra="ignore"
    )

    data_dir: Path = PROJECT_ROOT / "data"
    llm_provider: str = "deepseek"
    llm_model: str = "deepseek-chat"
    llm_api_base: str = "https://api.deepseek.com"
    llm_api_key: SecretStr = Field(default=SecretStr(""), repr=False)

    @property
    def database_path(self) -> Path:
        data_dir = self.data_dir
        if not data_dir.is_absolute():
            data_dir = PROJECT_ROOT / data_dir
        return data_dir / "knowledge.db"
