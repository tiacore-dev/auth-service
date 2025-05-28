from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from tortoise.expressions import Q

from app.database.models import Restriction
from app.handlers.auth import get_current_user
from app.pydantic_models.restrictions_models import (
    RestrictionsListResponseSchema,
    RestrictionsSchema,
    restriction_filter_params,
)

restrictions_router = APIRouter()


@restrictions_router.get(
    "/all",
    response_model=RestrictionsListResponseSchema,
    summary="Получение списка разрешений с фильтрацией",
)
async def get_restrictions(
    filters: Annotated[dict, Depends(restriction_filter_params)],
    _: str = Depends(get_current_user),
):
    logger.info(f"Запрос на список разрешений: {filters}")

    query = Q()
    if filters.get("comment"):
        query &= Q(comment__icontains=filters["comment"])
    if filters.get("restriction_name"):
        query &= Q(name__icontains=filters["restriction_name"])

    order = filters.get("order")
    sort_by = filters.get("sort_by", "name")
    order_by = f"{'-' if order == 'desc' else ''}{sort_by}"

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await Restriction.filter(query).count()

    restrictions = [
        RestrictionsSchema(**p)
        for p in await Restriction.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values("id", "name", "comment")
    ]

    if not restrictions:
        logger.info("Список разрешений пуст")
    return RestrictionsListResponseSchema(total=total_count, restrictions=restrictions)
