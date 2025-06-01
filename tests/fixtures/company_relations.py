import pytest

from app.database.models import (
    Company,
    EntityCompanyRelation,
    LegalEntity,
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


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_entity_relation(seed_legal_entity: LegalEntity, seed_company: Company):
    entity = await LegalEntity.get_or_none(id=seed_legal_entity.id)
    company = await Company.get_or_none(id=seed_company.id)

    relation = await EntityCompanyRelation.create(
        company=company, legal_entity=entity, relation_type="buyer"
    )
    return relation
