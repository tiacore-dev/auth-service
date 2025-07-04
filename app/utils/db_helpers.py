from loguru import logger
from tortoise import Tortoise
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction


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
        logger.info("Создание тестовых данных...")

        # Приложения
        applications = {
            "crm_app": "CRM application",
            "observer_app": "Observer service",
            "auth_app": "Сервис аутентификации",
            "reference_app": "Сервис справочников",
            "contract_app": "Сервис договоров",
            "parcel_app": "Сервис накладных",
        }

        for app_id, name in applications.items():
            await Application.get_or_create(id=app_id, defaults={"name": name})

        await Company.get_or_create(name="Tiacore")

        # Роли
        for app_id in applications.keys():
            await Role.get_or_create(
                name=f"Администратор {applications[app_id]}",
                application_id=app_id,
                system_name="admin",
            )
            await Role.get_or_create(
                name=f"Пользователь {applications[app_id]}",
                application_id=app_id,
                system_name="user",
            )

        logger.info("✅ Тестовые данные успешно созданы.")
    except IntegrityError as e:
        logger.error(f"Ошибка целостности данных: {e}")
    except Exception:
        import traceback

        traceback.print_exc()
