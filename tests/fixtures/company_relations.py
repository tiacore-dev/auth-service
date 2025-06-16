import pytest

from app.database.models import (
    Company,
    Role,
    User,
    UserCompanyRelation,
)


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_company():
    """Добавляет тестового пользователя в базу перед тестом."""
    company = await Company.create(name="Test Company", description="Description")
    return company


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_relation(seed_user: User, seed_company: Company, seed_role_admin: Role):
    user = await User.get_or_none(id=seed_user.id)
    company = await Company.get_or_none(id=seed_company.id)
    role = await Role.get_or_none(id=seed_role_admin.id)
    relation = await UserCompanyRelation.create(company=company, user=user, role=role)
    return relation
