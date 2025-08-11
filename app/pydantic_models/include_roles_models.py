from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RoleIncludeRelationCreateSchema(BaseModel):
    parent_role_id: UUID = Field(..., description="UUID основной роли (например, Parcel Admin)")
    child_role_id: UUID = Field(..., description="UUID включённой роли (например, Base Admin)")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True


class RoleIncludeRelationSchema(BaseModel):
    id: UUID = Field(..., alias="role_include_relation_id")
    parent_role_id: UUID
    child_role_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True


class RoleIncludeRelationListResponseSchema(BaseModel):
    total: int
    relations: list[RoleIncludeRelationSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True


class RoleIncludeRelationResponseSchema(BaseModel):
    role_include_relation_id: UUID

    class Config:
        from_attributes = True


class RoleIncludeRelationEditSchema(BaseModel):
    parent_role_id: UUID | None = Field(None, description="UUID основной роли")
    child_role_id: UUID | None = Field(None, description="UUID включённой роли")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True


class RoleIncludeRelationFilterSchema(BaseModel):
    parent_role_id: UUID | None = Field(None, description="Фильтр по основной роли")
    child_role_id: UUID | None = Field(None, description="Фильтр по включённой роли")
    sort_by: Literal["created_at"] = Field("created_at", description="Поле сортировки")
    order: Literal["asc", "desc"] = Field("asc", description="asc/desc")
    page: int = Field(1, ge=1, description="Номер страницы")
    page_size: int = Field(10, ge=1, le=100, description="Размер страницы")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True
