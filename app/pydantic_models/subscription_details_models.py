from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class SubscriptionDetailsBaseSchema(BaseModel):
    subscription_id: UUID
    entity_name: str = Field(...)
    bd_table: str
    restriction: int
    description: Optional[str] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class SubscriptionDetailsCreateSchema(SubscriptionDetailsBaseSchema):
    pass


class SubscriptionDetailsResponseSchema(BaseModel):
    subscription_details_id: UUID


class SubscriptionDetailsUpdateSchema(BaseModel):
    subscription_id: Optional[UUID] = None
    entity_name: Optional[str] = Field(None)
    bd_table: Optional[str] = None
    restriction: Optional[int] = None
    description: Optional[str] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class SubscriptionDetailsSchema(SubscriptionDetailsBaseSchema):
    id: UUID = Field(..., alias="subscription_detail_id")
    created_at: datetime
    created_by: UUID
    modified_at: datetime
    modified_by: UUID

    class Config:
        from_attributes = True
        populate_by_name = True


class SubscriptionDetailsListResponseSchema(BaseModel):
    total: int
    details: List[SubscriptionDetailsSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def subscription_details_filter_params(
    subscription_id: Optional[UUID] = Query(None, description="ID подписки"),
    entity_name: Optional[str] = Query(None, description="Название сущности"),
    bd_table: Optional[str] = Query(None, description="Таблица БД"),
    restriction_min: Optional[int] = Query(None, description="Минимальное ограничение"),
    restriction_max: Optional[int] = Query(None, description="Максимальное ограничение"),
    sort_by: Optional[str] = Query("entity_name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "subscription_id": subscription_id,
        "entity_name": entity_name,
        "bd_table": bd_table,
        "restriction_min": restriction_min,
        "restriction_max": restriction_max,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
