import pytest

from app.database.models import (
    Application,
    LegalEntityType,
    Permission,
    Restriction,
    Role,
    RolePermissionRelation,
)


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_role_admin():
    role = await Role.create(system_name="admin", name="Администратор")
    return role


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_permission():
    permission = await Permission.create(
        id="test_permission", name="Тестовое разрешение"
    )
    return permission


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_restriction():
    restriction = await Restriction.create(
        id="test_restriction", name="Тестовое разрешение"
    )
    return restriction


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_role_permission_relation(
    seed_role_admin: Role, seed_permission: Permission, seed_application: Application
):
    role = await Role.get_or_none(id=seed_role_admin.id)
    permission = await Permission.get_or_none(id=seed_permission.id)
    application = await Application.get_or_none(id=seed_application.id)
    relation = await RolePermissionRelation.create(
        role=role, permission=permission, application=application
    )
    return relation


@pytest.fixture(scope="function")
async def seed_role_manager():
    role = await Role.create(name="manager")
    return role


@pytest.fixture(scope="function")
async def seed_role_user(seed_application):
    role = await Role.create(name="Пользователь", system_name="user")
    return role


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_legal_entity_type():
    """Создает тестовый тип юридического лица."""
    entity_type = await LegalEntityType.create(id="ooo", name="ООО")
    return entity_type
