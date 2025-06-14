from tortoise import Tortoise
from tortoise.transactions import in_transaction

from app.database.models import LegalEntity


async def drop_all_tables():
    conn = Tortoise.get_connection("default")
    tables = await conn.execute_query_dict("""
        SELECT tablename FROM pg_tables WHERE schemaname = 'public';
    """)
    async with in_transaction() as tx:
        for table in tables:
            await tx.execute_query(
                f'DROP TABLE IF EXISTS "{table["tablename"]}" CASCADE;'
            )


async def create_admin_user(settings):
    from app.database.models import User, create_user

    admin = await User.filter(email="admin").first()
    if not admin:
        admin = await create_user(
            email="admin",
            password=settings.PASSWORD,
            position="admin",
            full_name="Поликанова Виктория Сергеевна",
        )
    admin.is_superadmin = True
    await admin.save()


async def create_test_data():
    from app.database.models import Application, Company, Role

    try:
        await Application.get_or_create(
            id="crm_app", defaults={"name": "CRM application"}
        )
        await Application.get_or_create(id="observer_app", name="Observer service")
        await Application.get_or_create(id="auth_app", name="Сервис аутентификации")
        await Company.get_or_create(name="Tiacore")
        await Role.get_or_create(name="Администратор", system_name="admin")
        await Role.get_or_create(name="Пользователь", system_name="user")

    except Exception as e:
        print(f"Exception: {e}")


async def get_entities_by_query(query):
    total_count = await LegalEntity.filter(query).count()
    entities = (
        await LegalEntity.filter(query)
        .prefetch_related("entity_type", "entity_company_relations")
        .all()
        .values(
            "id",
            "full_name",
            "short_name",
            "inn",
            "kpp",
            "opf",
            "vat_rate",
            "address",
            "entity_type_id",
            "signer",
            "ogrn",
        )
    )
    return total_count, entities
