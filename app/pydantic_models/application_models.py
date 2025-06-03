from typing import List, Optional

from fastapi import Query
from pydantic import Field

from app.pydantic_models.clean_model import CleanableBaseModel


class ApplicationsSchema(CleanableBaseModel):
    id: str = Field(..., alias="application_id")
    name: str = Field(..., alias="application_name")
    description: Optional[str] = Field(None)
    is_active: bool = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class ApplicationsListResponseSchema(CleanableBaseModel):
    total: int
    applications: List[ApplicationsSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True


def application_filter_params(
    application_name: Optional[str] = Query(None, description="Фильтр по названию"),
    description: Optional[str] = Query(None, description="Комментарий к разрешению"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "application_name": application_name,
        "description": description,
        "page": page,
        "page_size": page_size,
    }
