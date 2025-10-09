from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    app_name: str = "ScalableFastastAPITemplate"
    debug: bool = False
    db_user: str = ""
    db_password: str = ""
    db_name: str = "test.db"

    @property
    def db_url(self):
        return f"sqlite:///./{self.db_name}"


config = Config()
