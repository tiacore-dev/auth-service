from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from tortoise.expressions import Q

from app.database.models import (
    Application,
    Permission,
    Restriction,
    Role,
    RolePermissionRelation,
)
from app.handlers.auth import require_superadmin
from app.pydantic_models.role_permission_relation_models import (
    RolePermissionRelationCreateSchema,
    RolePermissionRelationEditSchema,
    RolePermissionRelationListResponseSchema,
    RolePermissionRelationResponseSchema,
    RolePermissionRelationSchema,
    role_permission_filter_params,
)
from app.utils.validate_helpers import validate_exists

role_relation_router = APIRouter()


@role_relation_router.post(
    "/add",
    response_model=RolePermissionRelationResponseSchema,
    summary="Добавить связь роль-разрешение",
    status_code=status.HTTP_201_CREATED,
)
async def add_role_permission_relation(
    data: RolePermissionRelationCreateSchema,
    _: dict = Depends(require_superadmin),
):
    await validate_exists(Role, data.role_id, "Роль")
    await validate_exists(Permission, data.permission_id, "Разрешение")
    await validate_exists(Restriction, data.restriction_id, "Запрет")
    await validate_exists(Application, data.application_id, "Приложение")
    relation = await RolePermissionRelation.create(
        role_id=data.role_id,
        permission_id=data.permission_id,
        restriction_id=data.restriction_id,
        application_id=data.application_id,
    )
    return {"role_permission_id": str(relation.id)}


@role_relation_router.patch(
    "/{role_permission_id}",
    response_model=RolePermissionRelationResponseSchema,
    summary="Изменить связь роль-разрешение",
)
async def update_role_permission_relation(
    role_permission_id: UUID,
    data: RolePermissionRelationEditSchema,
    _: dict = Depends(require_superadmin),
):
    relation = await RolePermissionRelation.filter(id=role_permission_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    update_data = data.model_dump(exclude_unset=True)

    for field, model, label in [
        ("role_id", Role, "Роль"),
        ("permission_id", Permission, "Разрешение"),
        ("restriction_id", Restriction, "Запрет"),
        ("application_id", Application, "Приложение"),
    ]:
        if field in update_data:
            await validate_exists(model, update_data[field], label)

    relation.update_from_dict(update_data)
    await relation.save()

    return {"role_permission_id": str(relation.id)}


@role_relation_router.delete(
    "/{role_permission_id}",
    summary="Удалить связь роль-разрешение",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role_permission_relation(
    role_permission_id: UUID, _: dict = Depends(require_superadmin)
):
    relation = await RolePermissionRelation.filter(id=role_permission_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    await relation.delete()


@role_relation_router.get(
    "/all",
    response_model=RolePermissionRelationListResponseSchema,
    summary="Получение списка связей",
)
async def get_role_permission_relations(
    filters: dict = Depends(role_permission_filter_params),
    _: dict = Depends(require_superadmin),
):
    try:
        query = Q()
        if filters.get("role_id"):
            query &= Q(role_id=filters["role_id"])
        if filters.get("permission_id"):
            query &= Q(permission_id=filters["permission_id"])

        if filters.get("restriction_id"):
            query &= Q(restriction_id=filters["restriction_id"])

        total_count = await RolePermissionRelation.filter(query).count()

        sort_by = filters.get("sort_by", "act_date")
        order = filters.get("order", "asc").lower()
        if order not in ("asc", "desc"):
            raise HTTPException(
                status_code=422, detail="order должен быть 'asc' или 'desc'"
            )

        sort_field = sort_by if order == "asc" else f"-{sort_by}"

        relations = (
            await RolePermissionRelation.filter(query)
            .order_by(sort_field)
            .prefetch_related("role", "permission", "restriction", "application")
            .offset((filters["page"] - 1) * filters["page_size"])
            .limit(filters["page_size"])
        )

        return RolePermissionRelationListResponseSchema(
            total=total_count,
            relations=[
                RolePermissionRelationSchema(
                    role_permission_id=rel.id,
                    role_id=rel.role.id,
                    permission_id=rel.permission.id,
                    restriction_id=rel.restriction.id if rel.restriction else None,
                    application_id=rel.application.id,
                    created_at=rel.created_at,
                )
                for rel in relations
            ],
        )
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@role_relation_router.get(
    "/{role_permission_id}",
    response_model=RolePermissionRelationSchema,
    summary="Просмотр одной связи",
)
async def get_role_permission_relation(
    role_permission_id: UUID, _: dict = Depends(require_superadmin)
):
    rel = (
        await RolePermissionRelation.filter(id=role_permission_id)
        .prefetch_related("role", "permission", "restriction", "application")
        .first()
    )

    if not rel:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    return RolePermissionRelationSchema(
        role_permission_id=rel.id,
        role_id=rel.role.id,
        permission_id=rel.permission.id,
        restriction_id=rel.restriction.id if rel.restriction else None,
        application_id=rel.application.id,
        created_at=rel.created_at,
    )
