from typing import List, Optional

from fastapi import Query
from pydantic import UUID4, Field

from app.pydantic_models.clean_model import CleanableBaseModel


class CompanyCreateSchema(CleanableBaseModel):
    name: str = Field(..., min_length=3, max_length=100, alias="company_name")
    description: Optional[str] = Field(None, description="Описание компании")

    class Config:
        allow_population_by_field_name = True


class CompanyResponseSchema(CleanableBaseModel):
    company_id: UUID4

    class Config:
        allow_population_by_field_name = True


class CompanySchema(CleanableBaseModel):
    company_id: UUID4
    company_name: str
    description: Optional[str] = None


class CompanyListResponseSchema(CleanableBaseModel):
    total: int  # 🔥 Количество записей по фильтру
    # ✅ Используем `list`, а не `List[CompanySchema]`
    companies: List[CompanySchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True  # Разрешаем нестандартные типы


class CompanyEditSchema(CleanableBaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=100, alias="company_name"
    )
    description: Optional[str] = Field(None, description="Описание компании")


def company_filter_params(
    search: Optional[str] = Query(None, description="Фильтр по названию компании"),
    sort_by: Optional[str] = Query("company_name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="Порядок сортировки: asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "search": search,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
