from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.pydantic_models.user_company_relation_models import (
    UserCompanyRelationCreateSchema,
    UserCompanyRelationEditSchema,
    UserCompanyRelationFilterSchema,
    UserCompanyRelationListResponseSchema,
    UserCompanyRelationResponseSchema,
    UserCompanyRelationSchema,
)
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Application, Company, Role, User, UserCompanyRelation
from app.dependencies.permissions import with_permission_and_user_company_check
from app.handlers.depends import require_permission_in_context

relation_router = APIRouter()


@relation_router.post(
    "/add",
    response_model=UserCompanyRelationResponseSchema,
    summary="Добавить связь пользователя с компанией",
    status_code=status.HTTP_201_CREATED,
)
async def add_user_company_relation(
    data: UserCompanyRelationCreateSchema,
    context: dict = Depends(require_permission_in_context("add_user_company_relation")),
):
    await validate_exists(Role, data.role_id, "Роль")
    await validate_exists(User, data.user_id, "Пользователь")
    await validate_exists(Company, data.company_id, "Компания")
    await validate_exists(Application, data.application_id, "Приложение")

    if not context.get("is_superadmin"):
        is_related = await UserCompanyRelation.exists(
            user_id=context["user"], company_id=data.company_id
        )
        if not is_related:
            raise HTTPException(
                status_code=403, detail="Вы не имеете доступа к этой компании"
            )

    relation = await UserCompanyRelation.create(**data.model_dump())

    return {"user_company_id": str(relation.id)}


@relation_router.patch(
    "/{user_company_id}",
    response_model=UserCompanyRelationResponseSchema,
    summary="Изменить связь пользователя с компанией",
)
async def update_user_company_relation(
    user_company_id: UUID,
    data: UserCompanyRelationEditSchema,
    _=with_permission_and_user_company_check("edit_user_company_relation"),
):
    relation = await UserCompanyRelation.filter(id=user_company_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    update_data = data.model_dump(exclude_unset=True)

    # ✅ Проверка только тех полей, которые есть
    if "role_id" in update_data:
        await validate_exists(Role, update_data["role_id"], "Роль")
    if "user_id" in update_data:
        await validate_exists(User, update_data["user_id"], "Пользователь")
    if "company_id" in update_data:
        await validate_exists(Company, update_data["company_id"], "Компания")
    if "application_id" in update_data:
        await validate_exists(
            Application, update_data.get("application_id"), "Приложение"
        )

    await relation.update_from_dict(update_data)
    await relation.save()

    return {"user_company_id": str(relation.id)}


@relation_router.delete(
    "/{user_company_id}",
    summary="Удалить связь пользователя с компанией",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_company_relation(
    user_company_id: UUID,
    _=with_permission_and_user_company_check("delete_user_company_relation"),
):
    relation = await UserCompanyRelation.filter(id=user_company_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    await relation.delete()


@relation_router.get(
    "/all",
    response_model=UserCompanyRelationListResponseSchema,
    summary="Получение списка связей",
)
async def get_user_company_relations(
    filters: UserCompanyRelationFilterSchema = Depends(),
    context: dict = Depends(
        require_permission_in_context("get_all_user_company_relations")
    ),
):
    query = Q()
    if filters.user_id:
        query &= Q(user=filters.user_id)
    if context["is_superadmin"]:
        if filters.company_id:
            query &= Q(company_id=filters.company_id)
    else:
        query &= Q(company_id=context["company_id"])
    if filters.role_id:
        query &= Q(role=filters.role_id)
    if filters.application_id:
        query &= Q(application_id=filters.application_id)

    if filters.order not in ("asc", "desc"):
        raise HTTPException(
            status_code=422, detail="order должен быть 'asc' или 'desc'"
        )

    sort_field = filters.sort_by if filters.order == "asc" else f"-{filters.sort_by}"

    total_count = await UserCompanyRelation.filter(query).count()

    relations_raw = (
        await UserCompanyRelation.filter(query)
        .order_by(sort_field)
        .prefetch_related("user", "company", "role")
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
        .values(
            "id", "user_id", "company_id", "role_id", "created_at", "application_id"
        )
    )

    relations = [UserCompanyRelationSchema(**rel) for rel in relations_raw]

    return UserCompanyRelationListResponseSchema(total=total_count, relations=relations)


@relation_router.get(
    "/{user_company_id}",
    response_model=UserCompanyRelationSchema,
    summary="Просмотр одной связи",
)
async def get_user_company_relation(
    user_company_id: UUID,
    _=with_permission_and_user_company_check("view_user_company_relation"),
):
    relation = (
        await UserCompanyRelation.filter(id=user_company_id)
        .prefetch_related("user", "company", "role")
        .first()
        .values(
            "id", "user_id", "company_id", "role_id", "created_at", "application_id"
        )
    )

    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    return UserCompanyRelationSchema(**relation)
