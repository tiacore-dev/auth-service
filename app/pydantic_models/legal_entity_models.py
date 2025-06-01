from typing import List, Literal, Optional

from fastapi import HTTPException, Query
from pydantic import UUID4, Field, field_validator

from app.pydantic_models.clean_model import CleanableBaseModel


class LegalEntityCreateSchema(CleanableBaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=255)
    short_name: str = Field(..., min_length=3, max_length=100)
    inn: str = Field(..., min_length=10, max_length=12)
    kpp: Optional[str] = Field(None, min_length=9, max_length=9)
    opf: Optional[str] = Field(None)
    ogrn: str = Field(..., min_length=13, max_length=13)
    vat_rate: Optional[int] = Field(0, ge=0, le=100)
    address: str = Field(..., min_length=5, max_length=255)
    entity_type_id: Optional[str] = Field(
        None, description="ID типа юр. лица (внешний ключ)"
    )
    signer: Optional[str] = Field(None, min_length=3, max_length=255)
    company_id: UUID4 = Field(..., description="ID компании (внешний ключ), UUID4")
    relation_type: Literal["seller", "buyer"] = Field(...)
    description: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True
        populate_by_name = True


class LegalEntityINNCreateSchema(CleanableBaseModel):
    inn: str = Field(..., min_length=10, max_length=12)
    kpp: Optional[str] = Field(None, min_length=9, max_length=9)
    company_id: UUID4 = Field(..., description="ID компании (внешний ключ), UUID4")
    relation_type: Literal["seller", "buyer"] = Field(...)
    description: Optional[str] = Field(None, max_length=500)


class LegalEntitySchema(CleanableBaseModel):
    id: UUID4 = Field(..., alias="legal_entity_id")
    full_name: Optional[str] = Field(None)
    short_name: str
    inn: str
    kpp: Optional[str] = None
    ogrn: str
    opf: Optional[str] = None
    vat_rate: int
    address: str
    entity_type_id: Optional[str] = None
    signer: Optional[str]

    @field_validator("kpp", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        return v or None

    class Config:
        from_attributes = True
        populate_by_name = True


def inn_kpp_filter_params(
    inn: str = Query(..., description="Инн юр. лица"),
    kpp: Optional[str] = Query(None, description="Кпп юр. лица"),
):
    # Проверка, что ИНН состоит только из цифр
    if not inn.isdigit():
        raise HTTPException(status_code=400, detail="ИНН должен содержать только цифры")

    # Проверка, что КПП либо None, либо только цифры
    if kpp is not None and not kpp.isdigit():
        raise HTTPException(status_code=400, detail="КПП должен содержать только цифры")

    # Вариант 1: ИНН = 10 цифр и КПП = 9 цифр
    if len(inn) == 10:
        if kpp is None or len(kpp) != 9:
            raise HTTPException(
                status_code=400, detail="При ИНН из 10 цифр требуется КПП из 9 цифр"
            )
    # Вариант 2: ИНН = 12 цифр и КПП отсутствует
    elif len(inn) == 12:
        if kpp is not None:
            raise HTTPException(
                status_code=400, detail="При ИНН из 12 цифр КПП указывать не нужно"
            )
    else:
        raise HTTPException(
            status_code=400, detail="ИНН должен содержать либо 10, либо 12 цифр"
        )
    return {"inn": inn, "kpp": kpp}


class LegalEntityShortSchema(CleanableBaseModel):
    id: UUID4 = Field(..., alias="legal_entity_id")
    short_name: str = Field(..., alias="legal_entity_name")

    class Config:
        from_attributes = True
        populate_by_name = True


class LegalEntityResponseSchema(CleanableBaseModel):
    legal_entity_id: UUID4

    class Config:
        from_attributes = True


class LegalEntityListResponseSchema(CleanableBaseModel):
    total: int
    entities: List[LegalEntitySchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class LegalEntityEditSchema(CleanableBaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=255)
    short_name: Optional[str] = Field(None, min_length=3, max_length=100)
    inn: Optional[str] = None
    kpp: Optional[str] = None
    opf: Optional[str] = Field(None)
    ogrn: Optional[str] = Field(None)
    vat_rate: Optional[int] = None
    address: Optional[str] = None
    entity_type_id: Optional[str] = None
    signer: Optional[str] = None

    class Config:
        from_attributes = True


def legal_entity_filter_params(
    company_id: Optional[UUID4] = Query(None, description="Фильтр по компании"),
    entity_type_id: Optional[str] = Query(None, description="Фильтр по типу юр. лица"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="Порядок сортировки: asc/desc"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "company_id": company_id,
        "entity_type": entity_type_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
