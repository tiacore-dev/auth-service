import os
from enum import Enum
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

ENV_FILE = ".env.test" if os.getenv("CI") == "true" else ".env"
load_dotenv(dotenv_path=ENV_FILE)


class ConfigName(str, Enum):
    TEST = "Test"
    SERVER = "Server"
    DEV = "Development"
    PRODUCTION = "Production"
    DOCKER = "Docker"


class BaseConfig(BaseSettings):
    SECRET_KEY: str = "default_secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_EXPIRATION_HOURS: int = 2
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    LOG_LEVEL: str = "DEBUG"
    ALGORITHM: str = "HS256"

    PORT: int = 5015
    ALLOW_ORIGINS: list[str] = []
    FRONT_ORIGIN: str | None = None
    BACK_ORIGIN: str | None = None
    ORIGIN: str | None = None

    OTLP_ENDPOINT: str | None = None

    SMTP_SERVER: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None

    LOGIN: str | None = None
    PASSWORD: str = " "
    JWT_SECRET: str | None = None

    DOCKERHUB_USERNAME: str | None = None
    CONFIG_NAME: str = "DEVELOPMENT"
    BOT_TOKEN: str | None = None
    CHAT_ID: str | None = None
    REDIS_URL: str | None = None
    NGROK_TOKEN: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # <––– вот это добавь

    @property
    def db_url(self) -> str:
        raise NotImplementedError("db_url not implemented in base config")


class TestConfig(BaseConfig):
    TEST_DATABASE_URL: str = "sqlite://db.sqlite3"

    @property
    def db_url(self) -> str:
        return self.TEST_DATABASE_URL


class DockerConfig(BaseConfig):
    DOCKER_DATABASE_URL: str = "sqlite:///server.db"

    @property
    def db_url(self) -> str:
        return self.DOCKER_DATABASE_URL


class DevConfig(BaseConfig):
    DATABASE_URL: str = "sqlite:///server.db"

    @property
    def db_url(self) -> str:
        return self.DATABASE_URL


class ServerConfig(BaseConfig):
    DATABASE_URL: str = "sqlite:///server.db"

    @property
    def db_url(self) -> str:
        return self.DATABASE_URL


class ProdConfig(BaseConfig):
    DATABASE_URL: str = "sqlite:///server.db"

    @property
    def db_url(self) -> str:
        return self.DATABASE_URL


@lru_cache
def get_settings(config_name: str = "Development") -> BaseConfig:
    match ConfigName(config_name):
        case ConfigName.TEST:
            return TestConfig()
        case ConfigName.DEV:
            return DevConfig()
        case ConfigName.DOCKER:
            return DockerConfig()
        case ConfigName.PRODUCTION:
            return ProdConfig()
        case ConfigName.SERVER:
            return ServerConfig()
        case _:
            raise ValueError(f"❌ Unknown config_name: {config_name}")
