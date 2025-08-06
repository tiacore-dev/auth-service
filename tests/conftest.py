import pytest
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient
from loguru import logger
from tortoise import Tortoise

from app import create_app
from app.config import ConfigName, _load_settings
from app.database.models import Application, User
from app.handlers.auth import create_access_token, create_refresh_token, login_handler
from app.utils.db_helpers import drop_all_tables


@pytest.fixture(scope="session")
def test_settings():
    return _load_settings(ConfigName.TEST)


@pytest.fixture(scope="function")
async def test_app():
    app = create_app(config_name=ConfigName.TEST)
    FastAPICache.init(InMemoryBackend())
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac
    await Tortoise.close_connections()


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def setup_and_clean_db(test_settings):
    logger.info(f"db_url: {test_settings.db_url}, app: {test_settings.APP}")
    await Tortoise.init(
        config={
            "connections": {"default": test_settings.db_url},
            "apps": {
                "models": {
                    "models": ["app.database.models"],
                    "default_connection": "default",
                },
            },
        }
    )

    await Tortoise.generate_schemas()

    yield
    await drop_all_tables()  # 💥 удаляем все таблицы
    await Tortoise.close_connections()


pytest_plugins = [
    "tests.fixtures.names",
    "tests.fixtures.company_relations",
    "tests.fixtures.permissions",
    "tests.fixtures.subscriptions",
]


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_user():
    """Добавляет тестового пользователя в базу перед тестом."""
    user = await User.create_user(email="test_user", password="qweasdzcx", position="user", full_name="Test User")
    user.is_verified = True
    await user.save()
    return user


@pytest.mark.usefixtures("test_app")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_admin():
    """Добавляет тестового администратора в базу перед тестом."""
    admin = await User.create_user(
        email="test_admin",
        password="adminpass",
        position="admin",
        full_name="Test Admin",
    )
    admin.is_superadmin = True
    await admin.save()
    return admin


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def jwt_token_user(seed_user: User, seed_application: Application, test_settings):
    """Генерирует JWT токен для обычного пользователя."""
    token_data = {
        "sub": seed_user.email,
        "user_id": str(seed_user.id),
        "application_id": str(seed_application.id),
    }
    return {
        "access_token": create_access_token(token_data, test_settings, "access"),
        "refresh_token": create_refresh_token(token_data, test_settings, "refresh"),
    }


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def jwt_token_admin(seed_admin: User, seed_application: Application, test_settings):
    """Генерирует JWT токен для администратора."""
    token_data = {
        "sub": seed_admin.email,
    }
    return {
        "access_token": create_access_token(token_data, test_settings, "access"),
        "refresh_token": create_refresh_token(token_data, test_settings, "refresh"),
    }


@pytest.fixture
def get_token_for_user(test_settings):
    async def _get_token(user: User, password="123"):
        auth_result = await login_handler(user.email, password)
        if not auth_result:
            raise ValueError(f"Не удалось залогиниться: {user.email}")
        user_obj, _ = auth_result
        return create_access_token(
            {
                "sub": user_obj.email,
            },
            test_settings,
            "access",
        )

    return _get_token
