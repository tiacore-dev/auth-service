from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.expressions import Q

from app.database.models import CompanySubscription
from app.handlers.auth import require_superadmin
from app.pydantic_models.company_subscription_models import (
    CompanySubscriptionCreateSchema,
    CompanySubscriptionListResponseSchema,
    CompanySubscriptionResponseSchema,
    CompanySubscriptionSchema,
    CompanySubscriptionUpdateSchema,
    company_subscription_filter_params,
)

company_subscription_router = APIRouter()


@company_subscription_router.post(
    "/add",
    response_model=CompanySubscriptionResponseSchema,
    summary="Добавить подписку компании",
    status_code=status.HTTP_201_CREATED,
)
async def add_company_subscription(
    data: CompanySubscriptionCreateSchema,
    context: dict = Depends(require_superadmin),
):
    company_subscription = await CompanySubscription.create(
        created_by=context["user_id"],
        modified_by=context["user_id"],
        **data.model_dump(),
    )
    return CompanySubscriptionResponseSchema(company_subscription_id=company_subscription.id)


@company_subscription_router.patch(
    "/{company_subscription_id}",
    response_model=CompanySubscriptionResponseSchema,
    summary="Обновить подписку компании",
)
async def update_company_subscription(
    company_subscription_id: UUID,
    data: CompanySubscriptionUpdateSchema,
    context: dict = Depends(require_superadmin),
):
    sub = await CompanySubscription.filter(id=company_subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка компании не найдена")

    update_data = data.model_dump(exclude_unset=True)
    await sub.update_from_dict(update_data)
    sub.modified_by = context["user_id"]
    await sub.save()

    return CompanySubscriptionResponseSchema(company_subscription_id=sub.id)


@company_subscription_router.delete(
    "/{company_subscription_id}",
    summary="Удалить подписку компании",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company_subscription(
    company_subscription_id: UUID,
    context: dict = Depends(require_superadmin),
):
    sub = await CompanySubscription.filter(id=company_subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка компании не найдена")
    await sub.delete()
    return


@company_subscription_router.get(
    "/all",
    response_model=CompanySubscriptionListResponseSchema,
    summary="Список подписок компаний",
)
async def get_company_subscriptions(
    filters: dict = Depends(company_subscription_filter_params),
    _: dict = Depends(require_superadmin),
):
    query = Q()

    if filters.get("company_id"):
        query &= Q(company_id=filters["company_id"])
    if filters.get("subscription_id"):
        query &= Q(subscription_id=filters["subscription_id"])

    sort_by = filters.get("sort_by", "created_at")
    order = filters.get("order", "asc")
    sort_field = sort_by if order == "asc" else f"-{sort_by}"

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total = await CompanySubscription.filter(query).count()
    results = await CompanySubscription.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return CompanySubscriptionListResponseSchema(
        total=total,
        subscriptions=[CompanySubscriptionSchema.model_validate(obj, from_attributes=True) for obj in results],
    )


@company_subscription_router.get(
    "/{company_subscription_id}",
    response_model=CompanySubscriptionSchema,
    summary="Получить подписку компании по ID",
)
async def get_company_subscription_by_id(
    company_subscription_id: UUID,
    context: dict = Depends(require_superadmin),
):
    sub = await CompanySubscription.filter(id=company_subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка компании не найдена")

    return CompanySubscriptionSchema.model_validate(sub, from_attributes=True)
