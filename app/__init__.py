from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from tortoise import Tortoise

from app.config import ConfigName, get_settings
from app.database.add_permissions import add_initial_permissions
from app.database.config import TORTOISE_ORM
from app.logger import setup_logger
from app.routes import register_routes
from app.utils.db_helpers import create_admin_user, create_test_data


def create_app(config_name: ConfigName) -> FastAPI:
    settings = get_settings(config_name)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ✅ Используем твой конфиг напрямую
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas() if config_name == "Test" else None

        # ✅ ORM готова, можно работать с БД
        await add_initial_permissions()
        await create_admin_user(settings)
        await create_test_data()

        yield

        await Tortoise.close_connections()

    app = FastAPI(title="Tiacore Auth Service", lifespan=lifespan)
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
