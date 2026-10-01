from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

GEEMCP_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    GEE_PROJECT_ID: str

    model_config = SettingsConfigDict(env_file=GEEMCP_DIR / ".gee.env", extra="ignore")

    CREDENTIALS_PATH: Path = GEEMCP_DIR / "credentials"


setting = Settings()
