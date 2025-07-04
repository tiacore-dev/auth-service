from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    status,
)
from loguru import logger
from tiacore_lib.pydantic_models.company_models import (
    CompanyCreateSchema,
    CompanyEditSchema,
    CompanyListResponseSchema,
    CompanyResponseSchema,
    CompanySchema,
    company_filter_params,
)
from tiacore_lib.rabbit.models import EventType
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Application, Company, Role, User, UserCompanyRelation
from app.handlers.auth import get_current_user
from app.utils.event_builder import build_user_event

company_router = APIRouter()


@company_router.post(
    "/add",
    response_model=CompanyResponseSchema,
    summary="Добавление новой компании",
    status_code=status.HTTP_201_CREATED,
)
async def add_company(
    request: Request,
    data: CompanyCreateSchema = Body(),
    user_data: dict = Depends(get_current_user),
):
    logger.info(f"Создание компании: {data.model_dump()}")

    company = await Company.create(name=data.name, description=data.description)

    if not company:
        raise HTTPException(status_code=500, detail="Не удалось создать компанию")

    logger.success(f"Компания создана: {company.id}")
    user = await User.get_or_none(email=user_data["email"])
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if user.is_superadmin:
        return {"company_id": str(company.id)}
    await validate_exists(Application, data.application_id, "Приложение")

    role = await Role.get_or_none(
        system_name="admin", application_id=data.application_id
    )
    if role:
        await UserCompanyRelation.create(
            role=role,
            company=company,
            user=user,
            application_id=data.application_id,
        )
        event = await build_user_event(user, event_type=EventType.USER_UPDATED)
        await request.app.state.publisher.publish_event(event)

    return {"company_id": str(company.id)}


# ✅ 2. Изменение компании
@company_router.patch(
    "/{company_id}", response_model=CompanyResponseSchema, summary="Изменение компании"
)
async def edit_company(
    company_id: UUID = Path(
        ..., title="ID компании", description="ID изменяемой компании"
    ),
    data: CompanyEditSchema = Body(),
    _=Depends(get_current_user),
):
    logger.info(f"Обновление компании {company_id}")

    updated_rows = await Company.filter(id=company_id).update(
        **data.model_dump(exclude_unset=True)
    )

    if not updated_rows:
        raise HTTPException(status_code=404, detail="Компания не найдена")

    logger.success(f"Компания {company_id} успешно обновлена")
    return {"company_id": str(company_id)}


# ✅ 3. Удаление компании
@company_router.delete(
    "/{company_id}", summary="Удаление компании", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_company(
    company_id: UUID = Path(
        ..., title="ID компании", description="ID удаляемой компании"
    ),
    _=Depends(get_current_user),
):
    logger.info(f"Удаление компании: {company_id}")

    company = await Company.filter(id=company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    await company.delete()
    logger.success(f"Компания {company_id} успешно удалена")


@company_router.get(
    "/all",
    response_model=CompanyListResponseSchema,
    summary="Получение списка компаний с фильтрацией",
)
async def get_companies(
    application_id: str = Query("auth_app"),
    filters: dict = Depends(company_filter_params),
    user_data: dict = Depends(get_current_user),
):
    logger.info(f"Запрос списка компаний: {filters}")
    try:
        query = Q()

        user = await User.get_or_none(email=user_data["email"])
        if not user:
            raise HTTPException(status_code=500, detail="Пользователь не найден в базе")

        if not user.is_superadmin:
            related_company_ids = await UserCompanyRelation.filter(
                user=user, application_id=application_id
            ).values_list("company__id", flat=True)

            if not related_company_ids:
                return CompanyListResponseSchema(total=0, companies=[])

            query &= Q(id__in=related_company_ids)

        # 🔎 Фильтрация по названию
        if filters.get("search"):
            query &= Q(name__icontains=filters["search"])

        # 📊 Подсчёт и выборка
        total_count = await Company.filter(query).count()

        sort_column = filters.get("sort_by", "name")
        sort_column = "name" if sort_column == "company_name" else sort_column
        order_by = f"{'-' if filters.get('order') == 'desc' else ''}{sort_column}"

        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)

        companies = (
            await Company.filter(query)
            .order_by(order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .values("id", "name", "description")
        )

        return CompanyListResponseSchema(
            total=total_count,
            companies=[CompanySchema(**company) for company in companies],
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@company_router.get(
    "/{company_id}", response_model=CompanySchema, summary="Просмотр компании"
)
async def get_company(
    company_id: UUID = Path(
        ..., title="ID компании", description="ID просматриваемой компании"
    ),
    user_data: dict = Depends(get_current_user),
):
    logger.info(f"Запрос на просмотр компании: {company_id}")

    company = await Company.get_or_none(id=company_id).values(
        "id", "name", "description"
    )
    if company is None:
        logger.warning(f"Компания {company_id} не найдена")
        raise HTTPException(status_code=404, detail="Компания не найдена")
    user = await User.get_or_none(email=user_data["email"])
    relation = await UserCompanyRelation.filter(
        user=user, company_id=company_id
    ).exists()
    if not user or (not user.is_superadmin and not relation):
        raise HTTPException(status_code=403, detail="Нет доступа к этой компании")

    company_schema = CompanySchema(**company)

    logger.success(f"Найдена компания: {company_schema}")
    return company_schema
