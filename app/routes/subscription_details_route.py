from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.expressions import Q

from app.database.models import SubscriptionDetails
from app.handlers.auth import require_superadmin
from app.pydantic_models.subscription_details_models import (
    SubscriptionDetailsCreateSchema,
    SubscriptionDetailsListResponseSchema,
    SubscriptionDetailsResponseSchema,
    SubscriptionDetailsSchema,
    SubscriptionDetailsUpdateSchema,
    subscription_details_filter_params,
)

subscription_details_router = APIRouter()


@subscription_details_router.post(
    "/add",
    response_model=SubscriptionDetailsResponseSchema,
    summary="Добавить деталь подписки",
    status_code=status.HTTP_201_CREATED,
)
async def add_subscription_detail(
    data: SubscriptionDetailsCreateSchema,
    context: dict = Depends(require_superadmin),
):
    detail = await SubscriptionDetails.create(
        created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump()
    )
    return SubscriptionDetailsResponseSchema(subscription_details_id=detail.id)


@subscription_details_router.patch(
    "/{subscription_details_id}",
    response_model=SubscriptionDetailsResponseSchema,
    summary="Редактировать деталь подписки",
)
async def edit_subscription_detail(
    subscription_details_id: UUID,
    data: SubscriptionDetailsUpdateSchema,
    context: dict = Depends(require_superadmin),
):
    detail = await SubscriptionDetails.filter(id=subscription_details_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="Деталь подписки не найдена")

    update_data = data.model_dump(exclude_unset=True)
    await detail.update_from_dict(update_data)
    detail.modified_by = context["user_id"]
    await detail.save()

    return SubscriptionDetailsResponseSchema(subscription_details_id=detail.id)


@subscription_details_router.delete(
    "/{subscription_details_id}",
    summary="Удалить деталь подписки",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_subscription_detail(
    subscription_details_id: UUID,
    context: dict = Depends(require_superadmin),
):
    detail = await SubscriptionDetails.filter(id=subscription_details_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="Деталь подписки не найдена")
    await detail.delete()
    return


@subscription_details_router.get(
    "/all",
    response_model=SubscriptionDetailsListResponseSchema,
    summary="Получить список деталей подписки",
)
async def get_subscription_details(
    filters: dict = Depends(subscription_details_filter_params),
):
    query = Q()

    if filters.get("subscription_id"):
        query &= Q(subscription_id=filters["subscription_id"])

    if filters.get("entity_name"):
        query &= Q(entity_name__icontains=filters["entity_name"])

    if filters.get("bd_table"):
        query &= Q(bd_table__icontains=filters["bd_table"])

    if filters.get("restriction_min") is not None:
        query &= Q(restriction__gte=filters["restriction_min"])

    if filters.get("restriction_max") is not None:
        query &= Q(restriction__lte=filters["restriction_max"])

    sort_by = filters.get("sort_by", "entity_name")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await SubscriptionDetails.filter(query).count()
    details = await SubscriptionDetails.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return SubscriptionDetailsListResponseSchema(
        total=total_count,
        details=[SubscriptionDetailsSchema.model_validate(obj, from_attributes=True) for obj in details],
    )


@subscription_details_router.get(
    "/{subscription_details_id}",
    response_model=SubscriptionDetailsSchema,
    summary="Получить деталь подписки по ID",
)
async def get_subscription_detail_by_id(
    subscription_details_id: UUID,
):
    detail = await SubscriptionDetails.filter(id=subscription_details_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="Деталь подписки не найдена")

    return SubscriptionDetailsSchema.model_validate(detail, from_attributes=True)
