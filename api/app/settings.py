import os
from typing import Any

from pydantic import BaseSettings, Field

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root


class Settings(BaseSettings):
    echo: bool = Field(env="ECHO", default=False)
    POSTGRES_DB: str = Field(env="POSTGRES_DB", default="database")
    POSTGRES_HOST: str = Field(env="POSTGRES_HOST", default="localhost")
    POSTGRES_PORT: int = Field(env="POSTGRES_PORT", default=5432)
    POSTGRES_USER: str = Field(env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(env="POSTGRES_PASSWORD")
    # broker_url: AmqpDsn = Field(env="BROKER_URL")

    @property
    def database_settings(self) -> dict[str, Any]:
        """
        Get all settings for connection with database.
        """
        return {
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    class Config:
        env_file = ".env", f"{ROOT_DIR}/../.env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    match os.getenv("ENV"):
        case "view":
            return Settings(_env_file="../.env")  # type: ignore[call-arg]
        case _:
            return Settings()
