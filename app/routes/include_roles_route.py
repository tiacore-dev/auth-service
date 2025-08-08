from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Role, RoleIncludeRelation
from app.handlers.auth import require_superadmin
from app.pydantic_models.include_roles_models import (
    RoleIncludeRelationCreateSchema,
    RoleIncludeRelationEditSchema,
    RoleIncludeRelationFilterSchema,
    RoleIncludeRelationListResponseSchema,
    RoleIncludeRelationResponseSchema,
    RoleIncludeRelationSchema,
)

role_include_router = APIRouter()


# Вспомогательная функция для проверки циклов
async def check_no_cycle(parent_role_id: UUID, child_role_id: UUID):
    """
    Проверяет, не возникает ли цикл при добавлении связи parent → child.
    """
    visited = set()
    queue = [child_role_id]
    while queue:
        current = queue.pop()
        if current == parent_role_id:
            raise HTTPException(status_code=400, detail="Добавление этой связи создаст цикл в иерархии ролей.")
        children = await RoleIncludeRelation.filter(parent_role_id=current).values_list("child_role_id", flat=True)
        for ch in children:
            if ch not in visited:
                visited.add(ch)
                queue.append(ch)  # type: ignore


@role_include_router.post(
    "/add",
    response_model=RoleIncludeRelationResponseSchema,
    summary="Добавить включение роли",
    status_code=status.HTTP_201_CREATED,
)
async def add_role_include_relation(
    data: RoleIncludeRelationCreateSchema,
    context: dict = Depends(require_superadmin),
):
    await validate_exists(Role, data.parent_role_id, "Основная роль (parent)")
    await validate_exists(Role, data.child_role_id, "Включённая роль (child)")

    if data.parent_role_id == data.child_role_id:
        raise HTTPException(status_code=400, detail="Роль не может включать саму себя.")

    # Проверка на циклы
    await check_no_cycle(data.parent_role_id, data.child_role_id)

    # Не допускаем дублирования связей
    exists = await RoleIncludeRelation.exists(parent_role_id=data.parent_role_id, child_role_id=data.child_role_id)
    if exists:
        raise HTTPException(status_code=409, detail="Такая связь уже существует.")

    relation = await RoleIncludeRelation.create(
        created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump()
    )
    return {"role_include_relation_id": str(relation.id)}


@role_include_router.patch(
    "/{role_include_relation_id}",
    response_model=RoleIncludeRelationResponseSchema,
    summary="Изменить включение роли",
)
async def update_role_include_relation(
    role_include_relation_id: UUID,
    data: RoleIncludeRelationEditSchema,
    context: dict = Depends(require_superadmin),
):
    relation = await RoleIncludeRelation.filter(id=role_include_relation_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    update_data = data.model_dump(exclude_unset=True)

    # Проверка на изменение parent/child
    if "parent_role_id" in update_data:
        await validate_exists(Role, update_data["parent_role_id"], "Основная роль (parent)")
    if "child_role_id" in update_data:
        await validate_exists(Role, update_data["child_role_id"], "Включённая роль (child)")

    # Если изменяются parent/child, проверить на цикл и дубли
    new_parent_id = update_data.get("parent_role_id", relation.parent_role_id)  # type: ignore
    new_child_id = update_data.get("child_role_id", relation.child_role_id)  # type: ignore

    if new_parent_id == new_child_id:
        raise HTTPException(status_code=400, detail="Роль не может включать саму себя.")

    # Проверка на циклы
    await check_no_cycle(new_parent_id, new_child_id)

    # Не допускаем дублирования (кроме текущей связи)
    exists = (
        await RoleIncludeRelation.filter(parent_role_id=new_parent_id, child_role_id=new_child_id)
        .exclude(id=role_include_relation_id)
        .exists()
    )
    if exists:
        raise HTTPException(status_code=409, detail="Такая связь уже существует.")

    await relation.update_from_dict(update_data)
    relation.modified_by = context["user_id"]
    await relation.save()
    return {"role_include_relation_id": str(relation.id)}


@role_include_router.delete(
    "/{role_include_relation_id}",
    summary="Удалить включение роли",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role_include_relation(
    role_include_relation_id: UUID,
    _: dict = Depends(require_superadmin),
):
    relation = await RoleIncludeRelation.filter(id=role_include_relation_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    await relation.delete()


@role_include_router.get(
    "/all",
    response_model=RoleIncludeRelationListResponseSchema,
    summary="Получение списка связей включения ролей",
)
async def get_role_include_relations(
    filters: RoleIncludeRelationFilterSchema = Depends(),
    _: dict = Depends(require_superadmin),
):
    query = Q()
    if filters.parent_role_id:
        query &= Q(parent_role_id=filters.parent_role_id)
    if filters.child_role_id:
        query &= Q(child_role_id=filters.child_role_id)
    if filters.order not in ("asc", "desc"):
        raise HTTPException(status_code=422, detail="order должен быть 'asc' или 'desc'")

    sort_field = filters.sort_by if filters.order == "asc" else f"-{filters.sort_by}"

    total_count = await RoleIncludeRelation.filter(query).count()
    relations_raw = (
        await RoleIncludeRelation.filter(query)
        .order_by(sort_field)
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
        .all()
    )
    relations = [RoleIncludeRelationSchema.model_validate(relation) for relation in relations_raw]
    return RoleIncludeRelationListResponseSchema(total=total_count, relations=relations)


@role_include_router.get(
    "/{role_include_relation_id}",
    response_model=RoleIncludeRelationSchema,
    summary="Просмотр одной связи включения ролей",
)
async def get_role_include_relation(
    role_include_relation_id: UUID,
    _: dict = Depends(require_superadmin),
):
    relation = await RoleIncludeRelation.filter(id=role_include_relation_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    return RoleIncludeRelationSchema.model_validate(relation)
