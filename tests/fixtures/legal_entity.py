import pytest

from app.database.models import (
    Company,
    EntityCompanyRelation,
    LegalEntity,
    LegalEntityType,
)


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_legal_entity(
    seed_company: Company, seed_legal_entity_type: LegalEntityType
):
    company = await Company.get_or_none(id=seed_company.id)
    entity_type = await LegalEntityType.get_or_none(id=seed_legal_entity_type.id)

    if not company or not entity_type:
        raise ValueError(
            "Ошибка: Не удалось получить объекты Company или LegalEntityType"
        )

    legal_entity = await LegalEntity.create(
        short_name="Test Legal Entity",
        inn="1234567890",
        kpp="123456789",
        vat_rate=20,
        ogrn="1027700132195",
        address="Test Address",
        entity_type=entity_type,
        signer="Test Signer",
    )

    # Создаем связь entity ↔ company
    await EntityCompanyRelation.create(
        company=company,
        legal_entity=legal_entity,
        relation_type="seller",
    )

    return legal_entity


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_legal_entity_buyer(
    seed_company: Company, seed_legal_entity_type: LegalEntityType
):
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""

    # Получаем объекты из базы
    company = await Company.get_or_none(id=seed_company.id)
    entity_type = await LegalEntityType.get_or_none(id=seed_legal_entity_type.id)

    if not company or not entity_type:
        raise ValueError(
            "Ошибка: Не удалось получить объекты Company или LegalEntityType"
        )

    # Создаем юридическое лицо, передавая объекты
    legal_entity = await LegalEntity.create(
        short_name="Test Legal Entity Buyer",
        inn="123456789013",
        kpp="123456789",
        vat_rate=20,
        ogrn="1027700132185",
        address="Test Address",
        entity_type=entity_type,
        signer="Test Signer",
    )

    await EntityCompanyRelation.create(
        legal_entity=legal_entity, company=company, relation_type="buyer"
    )

    return legal_entity
