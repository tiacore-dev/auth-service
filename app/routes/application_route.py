from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from tortoise.expressions import Q

from app.database.models import Application
from app.handlers.auth import get_current_user
from app.pydantic_models.application_models import (
    ApplicationsListResponseSchema,
    ApplicationsSchema,
    application_filter_params,
)

application_router = APIRouter()


@application_router.get(
    "/all",
    response_model=ApplicationsListResponseSchema,
    summary="Получение списка разрешений с фильтрацией",
)
async def get_applications(
    filters: Annotated[dict, Depends(application_filter_params)],
    _: str = Depends(get_current_user),
):
    logger.info(f"Запрос на список приложений: {filters}")

    query = Q()
    if filters.get("description"):
        query &= Q(description__icontains=filters["description"])
    if filters.get("application_name"):
        query &= Q(name__icontains=filters["application_name"])

    order = filters.get("order")
    sort_by = filters.get("sort_by", "name")
    order_by = f"{'-' if order == 'desc' else ''}{sort_by}"

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await Application.filter(query).count()

    applications = [
        ApplicationsSchema(**p)
        for p in await Application.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values("id", "name", "description", "is_active")
    ]

    if not applications:
        logger.info("Список разрешений пуст")
    return ApplicationsListResponseSchema(total=total_count, applications=applications)
