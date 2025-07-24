from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_client import make_asgi_app
from tiacore_lib.config import ConfigName, get_settings
from tiacore_lib.rabbit.publisher import EventPublisher
from tortoise import Tortoise

from app.config import TestConfig, _load_settings
from app.database.add_permissions import add_initial_permissions
from app.logger import setup_logger
from app.routes import register_routes
from app.utils.db_helpers import create_test_data


def provide_settings(config_name: ConfigName):
    def _inner():
        return _load_settings(config_name)

    return _inner


def create_app(config_name: ConfigName) -> FastAPI:
    settings = _load_settings(config_name)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("🔥 Lifespan START")
        print(f"Тип настроек: {type(settings)}")
        if not isinstance(settings, TestConfig):
            from app.database.config import TORTOISE_ORM

            await Tortoise.init(config=TORTOISE_ORM)

            Tortoise.init_models(["app.database.models"], "models")

            await add_initial_permissions()
            # await create_admin_user(settings)
            await create_test_data()
            redis_url = settings.REDIS_URL
            redis_client = redis.from_url(redis_url)
            FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

            app.state.publisher = EventPublisher(settings.AUTH_BROKER_URL)
            await app.state.publisher.connect()
        yield

        await Tortoise.close_connections()

    app = FastAPI(title="Auth Service", lifespan=lifespan)
    app.dependency_overrides[get_settings] = provide_settings(config_name)
    setup_logger()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/metrics", make_asgi_app())

    if config_name in {ConfigName.PRODUCTION, ConfigName.SERVER}:
        from app.tracer import init_tracer

        init_tracer(app)

    register_routes(app)

    return app
