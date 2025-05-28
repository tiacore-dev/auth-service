from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from tortoise.expressions import Q

from app.database.models import Company, Role, User, UserCompanyRelation
from app.dependencies.permissions import with_exact_company_permission
from app.handlers.auth import get_current_user
from app.pydantic_models.company_models import (
    CompanyCreateSchema,
    CompanyEditSchema,
    CompanyListResponseSchema,
    CompanyResponseSchema,
    CompanySchema,
    company_filter_params,
)

company_router = APIRouter()


@company_router.post(
    "/add",
    response_model=CompanyResponseSchema,
    summary="Добавление новой компании",
    status_code=status.HTTP_201_CREATED,
)
async def add_company(
    data: CompanyCreateSchema = Body(), user_data: dict = Depends(get_current_user)
):
    logger.info(f"Создание компании: {data.model_dump()}")
    try:
        company = await Company.create(name=data.name, description=data.description)

        if not company:
            raise HTTPException(status_code=500, detail="Не удалось создать компанию")

        logger.success(f"Компания создана: {company.id}")
        role = await Role.get_or_none(system_name="admin")
        user = await User.get_or_none(email=user_data["email"])
        if role and user:
            await UserCompanyRelation.create(role=role, company=company, user=user)

        return {"company_id": str(company.id)}

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


# ✅ 2. Изменение компании
@company_router.patch(
    "/{company_id}", response_model=CompanyResponseSchema, summary="Изменение компании"
)
async def edit_company(
    company_id: UUID = Path(
        ..., title="ID компании", description="ID изменяемой компании"
    ),
    data: CompanyEditSchema = Body(),
    _=with_exact_company_permission("edit_company"),
):
    logger.info(
        f"Обновление компании {company_id}: {data.model_dump(exclude_unset=True)}"
    )
    try:
        updated_rows = await Company.filter(id=company_id).update(
            **data.model_dump(exclude_unset=True)
        )

        if not updated_rows:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        logger.success(f"Компания {company_id} успешно обновлена")
        return {"company_id": str(company_id)}

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


# ✅ 3. Удаление компании
@company_router.delete(
    "/{company_id}", summary="Удаление компании", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_company(
    company_id: UUID = Path(
        ..., title="ID компании", description="ID удаляемой компании"
    ),
    _=with_exact_company_permission("delete_company"),
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
            # 🔍 Получаем список компаний, к которым у пользователя есть доступ
            related_company_ids = await UserCompanyRelation.filter(
                user=user
            ).values_list("company__company_id", flat=True)

            if not related_company_ids:
                return CompanyListResponseSchema(total=0, companies=[])

            query &= Q(company_id__in=related_company_ids)

        # 🔎 Фильтрация по названию
        if filters.get("search"):
            query &= Q(name__icontains=filters["search"])

        # 📊 Подсчёт и выборка
        total_count = await Company.filter(query).count()

        sort_column = filters.get("sort_by", "company_name")
        sort_column = "name" if sort_column == "company_name" else sort_column
        order_by = f"{'-' if filters.get('order') == 'desc' else ''}{sort_column}"

        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)

        companies = (
            await Company.filter(query)
            .order_by(order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return CompanyListResponseSchema(
            total=total_count,
            companies=[
                CompanySchema(
                    company_id=company.id,
                    company_name=company.name,
                    description=company.description,
                )
                for company in companies
            ],
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
    try:
        company = await Company.get_or_none(id=company_id)
        if company is None:
            logger.warning(f"Компания {company_id} не найдена")
            raise HTTPException(status_code=404, detail="Компания не найдена")
        user = await User.get_or_none(email=user_data["email"])
        relation = await UserCompanyRelation.filter(
            user=user, company_id=company_id
        ).exists()
        if not user or (not user.is_superadmin and not relation):
            raise HTTPException(status_code=403, detail="Нет доступа к этой компании")

        company_schema = CompanySchema(
            company_id=company.id,
            company_name=company.name,
            description=company.description,
        )

        logger.success(f"Найдена компания: {company_schema}")
        return company_schema

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e
