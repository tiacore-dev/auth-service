from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from tortoise.expressions import Q

from app.database.models import Permission
from app.handlers.auth import get_current_user
from app.pydantic_models.permissions_models import (
    PermissionsListResponseSchema,
    PermissionsSchema,
    permission_filter_params,
)

permissions_router = APIRouter()


@permissions_router.get(
    "/all",
    response_model=PermissionsListResponseSchema,
    summary="Получение списка разрешений с фильтрацией",
)
async def get_permissions(
    filters: Annotated[dict, Depends(permission_filter_params)],
    _: str = Depends(get_current_user),
):
    logger.info(f"Запрос на список разрешений: {filters}")

    query = Q()
    if filters.get("comment"):
        query &= Q(comment__icontains=filters["comment"])
    if filters.get("permission_name"):
        query &= Q(name__icontains=filters["permission_name"])

    order = filters.get("order")
    sort_by = filters.get("sort_by", "name")
    order_by = f"{'-' if order == 'desc' else ''}{sort_by}"

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await Permission.filter(query).count()

    permissions = [
        PermissionsSchema(**p)
        for p in await Permission.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values("id", "name", "comment")
    ]

    if not permissions:
        logger.info("Список разрешений пуст")
    return PermissionsListResponseSchema(total=total_count, permissions=permissions)
