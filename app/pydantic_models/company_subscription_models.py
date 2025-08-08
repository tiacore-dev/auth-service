from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class CompanySubscriptionBaseSchema(BaseModel):
    user_id: UUID
    company_id: UUID
    subscription_id: UUID

    class Config:
        from_attributes = True


class CompanySubscriptionCreateSchema(CompanySubscriptionBaseSchema):
    pass


class CompanySubscriptionUpdateSchema(BaseModel):
    user_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    subscription_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class CompanySubscriptionResponseSchema(BaseModel):
    company_subscription_id: UUID


class CompanySubscriptionSchema(CompanySubscriptionBaseSchema):
    id: UUID = Field(..., alias="company_subscription_id")

    created_at: datetime
    created_by: UUID
    modified_at: datetime
    modified_by: UUID

    class Config:
        from_attributes = True
        populate_by_name = True


class CompanySubscriptionListResponseSchema(BaseModel):
    total: int
    subscriptions: List[CompanySubscriptionSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def company_subscription_filter_params(
    user_id: Optional[UUID] = Query(None, description="ID пользователя"),
    company_id: Optional[UUID] = Query(None, description="ID компании"),
    subscription_id: Optional[UUID] = Query(None, description="ID подписки"),
    sort_by: Literal["created_at"] = Query("created_at", description="Поле сортировки"),
    order: Literal["asc", "desc"] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "user_id": user_id,
        "company_id": company_id,
        "subscription_id": subscription_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
