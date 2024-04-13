from typing import Any

from pydantic import AnyHttpUrl, BaseSettings, Field


class Settings(BaseSettings):
    POSTGRES_DB: str = Field(env="POSTGRES_DB", default="database")
    POSTGRES_HOST: str = Field(env="POSTGRES_HOST", default="localhost")
    POSTGRES_USER: str = Field(env="POSTGRES_USER", default="myusername")
    POSTGRES_PORT: int = Field(env="POSTGRES_PORT", default=5432)
    POSTGRES_PASSWORD: str = Field(env="POSTGRES_PASSWORD", default="mypassword")
    api_url: AnyHttpUrl = Field(env="API_URL")
    logger_level: int = Field(env="LOGGER_LEVEL", default=10)
    vk_token: str = Field(env="VK_TOKEN")
    selenium_hub: AnyHttpUrl | None = Field(env="SELENIUM_HUB")
    sleep: int = Field(env="SLEEP", default=60)
    docker: bool = Field(env="DOCKER", default=False)

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
    def database_url(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()
