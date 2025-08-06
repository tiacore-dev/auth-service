import os

from dotenv import load_dotenv

from app.config import ConfigName, _load_settings

load_dotenv()


CONFIG_NAME = ConfigName(os.getenv("CONFIG_NAME", "development"))
settings = _load_settings(config_name=CONFIG_NAME)

TORTOISE_ORM = {
    "connections": {"default": settings.db_url},
    "apps": {
        "models": {
            # Укажите только модуль
            "models": ["app.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
