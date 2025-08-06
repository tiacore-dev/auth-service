from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.expressions import Q

from app.database.models import SubscriptionPayments
from app.handlers.auth import require_superadmin
from app.pydantic_models.subscription_payments_models import (
    SubscriptionPaymentCreateSchema,
    SubscriptionPaymentListResponseSchema,
    SubscriptionPaymentResponseSchema,
    SubscriptionPaymentSchema,
    SubscriptionPaymentUpdateSchema,
    subscription_payment_filter_params,
)

subscription_payment_router = APIRouter()


@subscription_payment_router.post(
    "/add",
    response_model=SubscriptionPaymentResponseSchema,
    summary="Добавить оплату по подписке",
    status_code=status.HTTP_201_CREATED,
)
async def add_subscription_payment(
    data: SubscriptionPaymentCreateSchema,
    context: dict = Depends(require_superadmin),
):
    payment = await SubscriptionPayments.create(
        created_by=context["user_id"],
        modified_by=context["user_id"],
        **data.model_dump(),
    )
    return SubscriptionPaymentResponseSchema(subscription_payment_id=payment.id)


@subscription_payment_router.patch(
    "/{subscription_payment_id}",
    response_model=SubscriptionPaymentResponseSchema,
    summary="Обновить оплату подписки",
)
async def update_subscription_payment(
    subscription_payment_id: UUID,
    data: SubscriptionPaymentUpdateSchema,
    context: dict = Depends(require_superadmin),
):
    payment = await SubscriptionPayments.filter(id=subscription_payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не найдена")

    update_data = data.model_dump(exclude_unset=True)
    await payment.update_from_dict(update_data)
    payment.modified_by = context["user_id"]
    await payment.save()

    return SubscriptionPaymentResponseSchema(subscription_payment_id=payment.id)


@subscription_payment_router.delete(
    "/{subscription_payment_id}",
    summary="Удалить оплату подписки",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_subscription_payment(
    subscription_payment_id: UUID,
    context: dict = Depends(require_superadmin),
):
    payment = await SubscriptionPayments.filter(id=subscription_payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не найдена")

    await payment.delete()
    return


@subscription_payment_router.get(
    "/all",
    response_model=SubscriptionPaymentListResponseSchema,
    summary="Получить список оплат по подписке компании",
)
async def get_subscription_payments(
    filters: dict = Depends(subscription_payment_filter_params),
    _: dict = Depends(require_superadmin),
):
    query = Q()

    if filters.get("company_subscription_id"):
        query &= Q(company_subscription_id=filters["company_subscription_id"])
    if filters.get("payment_date_from"):
        query &= Q(payment_date__gte=filters["payment_date_from"])
    if filters.get("payment_date_to"):
        query &= Q(payment_date__lte=filters["payment_date_to"])
    if filters.get("date_from"):
        query &= Q(date_from__gte=filters["date_from"])
    if filters.get("date_to"):
        query &= Q(date_to__lte=filters["date_to"])

    sort_by = filters.get("sort_by", "payment_date")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total = await SubscriptionPayments.filter(query).count()
    payments = await SubscriptionPayments.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return SubscriptionPaymentListResponseSchema(
        total=total,
        payments=[SubscriptionPaymentSchema.model_validate(p, from_attributes=True) for p in payments],
    )


@subscription_payment_router.get(
    "/{subscription_payment_id}",
    response_model=SubscriptionPaymentSchema,
    summary="Получить оплату подписки по ID",
)
async def get_subscription_payment_by_id(
    subscription_payment_id: UUID,
    context: dict = Depends(require_superadmin),
):
    payment = await SubscriptionPayments.filter(id=subscription_payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не найдена")

    return SubscriptionPaymentSchema.model_validate(payment, from_attributes=True)
