from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class SubscriptionPaymentBaseSchema(BaseModel):
    company_subscription_id: UUID
    payment_external_id: Optional[str] = None
    payment_date: date
    payment_amount: float
    date_from: date
    date_to: date

    class Config:
        from_attributes = True


class SubscriptionPaymentCreateSchema(SubscriptionPaymentBaseSchema):
    pass


class SubscriptionPaymentUpdateSchema(BaseModel):
    company_subscription_id: Optional[UUID] = None
    payment_external_id: Optional[str] = None
    payment_date: Optional[date] = None
    payment_amount: Optional[float] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    class Config:
        from_attributes = True


class SubscriptionPaymentResponseSchema(BaseModel):
    subscription_payment_id: UUID


class SubscriptionPaymentSchema(SubscriptionPaymentBaseSchema):
    id: UUID = Field(..., alias="subscription_payment_id")
    created_at: datetime
    created_by: UUID
    modified_at: datetime
    modified_by: UUID

    class Config:
        from_attributes = True
        populate_by_name = True


class SubscriptionPaymentListResponseSchema(BaseModel):
    total: int
    payments: List[SubscriptionPaymentSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def subscription_payment_filter_params(
    company_subscription_id: Optional[UUID] = Query(None, description="ID подписки компании"),
    payment_date_from: Optional[date] = Query(None, description="Дата оплаты от"),
    payment_date_to: Optional[date] = Query(None, description="Дата оплаты до"),
    date_from: Optional[date] = Query(None, description="Начало периода действия"),
    date_to: Optional[date] = Query(None, description="Конец периода действия"),
    sort_by: Optional[str] = Query("payment_date", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "company_subscription_id": company_subscription_id,
        "payment_date_from": payment_date_from,
        "payment_date_to": payment_date_to,
        "date_from": date_from,
        "date_to": date_to,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
