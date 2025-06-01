from typing import List, Optional

from fastapi import Query
from pydantic import Field

from app.pydantic_models.clean_model import CleanableBaseModel


class LegalEntityTypeSchema(CleanableBaseModel):
    id: str = Field(..., alias="legal_entity_type_id")
    name: str = Field(..., alias="entity_type_name")

    class Config:
        from_attributes = True
        populate_by_name = True


class LegalEntityTypeListResponse(CleanableBaseModel):
    total: int
    legal_entity_types: List[LegalEntityTypeSchema]


# ✅ Фильтры и параметры поиска
class FilterParams(CleanableBaseModel):
    entity_name: Optional[str] = Query(None, description="Фильтр по названию")
    sort_by: str = Query("name", description="Сортировка (по умолчанию name)")
    order: str = Query("asc", description="Порядок сортировки: asc/desc")
    page: int = Query(1, description="Номер страницы")
    page_size: int = Query(10, description="Размер страницы")
