from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.expressions import Q

from app.database.models import Subscription
from app.handlers.auth import require_superadmin
from app.pydantic_models.subscription_models import (
    SubscriptionCreateSchema,
    SubscriptionListResponseSchema,
    SubscriptionResponseSchema,
    SubscriptionSchema,
    SubscriptionUpdateSchema,
    subscription_filter_params,
)

subscription_router = APIRouter()


@subscription_router.post(
    "/add",
    response_model=SubscriptionResponseSchema,
    summary="Добавить подписку",
    status_code=status.HTTP_201_CREATED,
)
async def add_subscription(
    data: SubscriptionCreateSchema,
    context: dict = Depends(require_superadmin),
):
    subscription = await Subscription.create(
        created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump()
    )
    return SubscriptionResponseSchema(subscription_id=subscription.id)


@subscription_router.patch(
    "/{subscription_id}",
    response_model=SubscriptionResponseSchema,
    summary="Редактировать подписку",
)
async def edit_subscription(
    subscription_id: UUID,
    data: SubscriptionUpdateSchema,
    context: dict = Depends(require_superadmin),
):
    subscription = await Subscription.filter(id=subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    update_data = data.model_dump(exclude_unset=True)
    await subscription.update_from_dict(update_data)
    subscription.modified_by = context["user_id"]
    await subscription.save()

    return SubscriptionResponseSchema(subscription_id=subscription.id)


@subscription_router.delete(
    "/{subscription_id}",
    summary="Удалить подписку",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_subscription(
    subscription_id: UUID,
    context: dict = Depends(require_superadmin),
):
    subscription = await Subscription.filter(id=subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    await subscription.delete()
    return


@subscription_router.get(
    "/all",
    response_model=SubscriptionListResponseSchema,
    summary="Получить список подписок",
)
async def get_subscriptions(
    filters: dict = Depends(subscription_filter_params),
):
    query = Q()

    if filters.get("subscription_name"):
        query &= Q(name__icontains=filters["subscription_name"])

    if filters.get("application_id"):
        query &= Q(application_id=filters["application_id"])

    if filters.get("price_min") is not None:
        query &= Q(price__gte=filters["price_min"])
    if filters.get("price_max") is not None:
        query &= Q(price__lte=filters["price_max"])

    sort_by = filters.get("sort_by", "created_at")
    if sort_by == "subscription_name":
        sort_by = "name"

    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await Subscription.filter(query).count()
    subscriptions = await Subscription.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return SubscriptionListResponseSchema(
        total=total_count,
        subscriptions=[SubscriptionSchema.model_validate(obj, from_attributes=True) for obj in subscriptions],
    )


@subscription_router.get(
    "/{subscription_id}",
    response_model=SubscriptionSchema,
    summary="Получить подписку по ID",
)
async def get_subscription_by_id(
    subscription_id: UUID,
):
    subscription = await Subscription.filter(id=subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    return SubscriptionSchema.model_validate(subscription, from_attributes=True)
