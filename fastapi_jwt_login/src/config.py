from pathlib import Path
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if not ENV_FILE.exists():
    raise FileNotFoundError(f"❌ .env file not found at: {ENV_FILE}")


class Settings(BaseSettings):
    algorithm: str = Field(..., alias="ALGORITHM")
    database_url: str = f"sqlite:///{BASE_DIR}/db.sqlite3"
    secret_key: SecretStr = Field(..., alias="SECRET_KEY")
    DATABASE_CONNECT_DICT: dict = {}
    csrf_secret: str = Field(..., alias="CSRF_SECRET")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
        env_file_encoding="utf-8",
        case_sensitive=True,
        # ensure correct path
    )

    def debug(self):
        print("Loaded settings:", self.model_dump())


settings = Settings()
