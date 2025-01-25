import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

import clicky

load_dotenv(Path(__file__).parent / f'{os.environ.get("ENV", "local")}.env')

APP_DIR = Path(clicky.__file__).resolve().parent.parent


class ClickhouseSettings(BaseSettings):
    """
    Temporary until we save connections in the database.
    """

    CLICKHOUSE_HOST: str
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DB: str


class Settings(BaseSettings):
    ROOT_PATH: str = ""
    SERVER_PORT: int = 8080
    SERVER_HOST: str = "0.0.0.0"
    PROJECT_NAME: str = "Clicky"
    DEVELOPMENT_MODE: bool = False

    STATIC_DIR: Path = APP_DIR / "static"
    TEMPLATES_DIR: Path = APP_DIR / "templates"

    LOG_CONFIG_FILE: Path | None = None
    """
    Optional path to a Python logging configuration file.
    If not provided, the default logging configuration is used.
    """

    OPENAI_API_KEY: str
    SQLITE_DB_URL: str = "sqlite+aiosqlite:///./data/clicky.db"


settings = Settings()  # type: ignore[call-arg]
clickhouse_settings = ClickhouseSettings()  # type: ignore[call-arg]
