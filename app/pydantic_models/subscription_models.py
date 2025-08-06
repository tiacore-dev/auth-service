from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class SubscriptionBaseSchema(BaseModel):
    name: str = Field(..., alias="subscription_name")
    price: float
    application_id: str
    description: Optional[str] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class SubscriptionCreateSchema(SubscriptionBaseSchema):
    pass


class SubscriptionResponseSchema(BaseModel):
    subscription_id: UUID


class SubscriptionUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, alias="subscription_name")
    price: Optional[float] = None
    application_id: Optional[str] = None
    description: Optional[str] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class SubscriptionSchema(SubscriptionBaseSchema):
    id: UUID = Field(..., alias="subscription_id")
    created_at: datetime
    created_by: UUID
    modified_at: datetime
    modified_by: UUID

    class Config:
        from_attributes = True
        populate_by_name = True


class SubscriptionListResponseSchema(BaseModel):
    total: int
    subscriptions: List[SubscriptionSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def subscription_filter_params(
    subscription_name: Optional[str] = Query(None, description="Название подписки"),
    application_id: Optional[UUID] = Query(None, description="ID приложения"),
    price_min: Optional[float] = Query(None, description="Минимальная цена"),
    price_max: Optional[float] = Query(None, description="Максимальная цена"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "subscription_name": subscription_name,
        "application_id": application_id,
        "price_min": price_min,
        "price_max": price_max,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
