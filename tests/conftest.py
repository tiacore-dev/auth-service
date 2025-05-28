import pytest
from httpx import AsyncClient
from tortoise import Tortoise

from app import create_app
from app.config import ConfigName, get_settings
from app.database.models import Application, User, create_user
from app.handlers.auth import create_access_token, create_refresh_token, login_handler
from app.utils.db_helpers import drop_all_tables


@pytest.fixture(scope="session")
async def test_app():
    app = create_app(config_name=ConfigName.TEST)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    await Tortoise.close_connections()


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def setup_and_clean_db():
    settings = get_settings(config_name=ConfigName.TEST)
    await Tortoise.init(
        config={
            "connections": {"default": settings.db_url},
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
]


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_user():
    """Добавляет тестового пользователя в базу перед тестом."""
    user = await create_user(
        email="test_user", password="qweasdzcx", position="user", full_name="Test User"
    )
    user.is_verified = True
    await user.save()
    return user


@pytest.mark.usefixtures("test_app")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_admin():
    """Добавляет тестового администратора в базу перед тестом."""
    admin = await create_user(
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
async def jwt_token_user(seed_user: User, seed_application: Application):
    """Генерирует JWT токен для обычного пользователя."""
    token_data = {
        "sub": seed_user.email,
        "user_id": str(seed_user.id),
        "application_id": str(seed_application.id),
    }
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
    }


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def jwt_token_admin(seed_admin: User, seed_application: Application):
    """Генерирует JWT токен для администратора."""
    token_data = {
        "sub": seed_admin.email,
        "user_id": str(seed_admin.id),
        "application_id": str(seed_application.id),
    }
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
    }


@pytest.fixture
def get_token_for_user(seed_application: Application):
    async def _get_token(user: User, password="123"):
        auth_result = await login_handler(user.email, password, seed_application.id)
        if not auth_result:
            raise ValueError(f"Не удалось залогиниться: {user.email}")
        user_obj, _ = auth_result
        return create_access_token(
            {
                "sub": user_obj.email,
                "application_id": str(seed_application.id),
                "user_id": str(user.id),
            }
        )

    return _get_token
