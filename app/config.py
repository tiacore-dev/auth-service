from pydantic_settings import SettingsConfigDict
from tiacore_lib.config import (
    BaseConfig as SharedBaseConfig,
    ConfigName,
    TestConfig as SharedTestConfig,
)


class BaseConfig(SharedBaseConfig):
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

    DOCKERHUB_USERNAME: str | None = None
    CONFIG_NAME: str = "DEVELOPMENT"

    AUTH_BROKER_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def db_url(self) -> str:
        raise NotImplementedError("db_url not implemented in base config")


class TestConfig(SharedTestConfig):
    TEST_DATABASE_URL: str = "sqlite://db.sqlite3"
    APP: str = "test_app"
    SECRET_KEY: str = "default_secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_EXPIRATION_HOURS: int = 2
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    SMTP_SERVER: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    FRONT_ORIGIN: str | None = None
    BACK_ORIGIN: str | None = None
    AUTH_BROKER_URL: str = ""
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="ignore",  # необязательно, но рекомендую
    )

    def __init__(self, **kwargs):
        print("✅ LOADING TestConfig")
        super().__init__(**kwargs)

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


def _load_settings(config_name: str):
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
