from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from loguru import logger
from tortoise.expressions import Q

from app.database.models import Role, RolePermissionRelation
from app.handlers.auth import get_current_user, require_superadmin
from app.pydantic_models.roles_models import (
    RoleCreateManySchema,
    RoleCreateSchema,
    RoleEditSchema,
    RoleFilterSchema,
    RoleListResponseSchema,
    RoleResponseSchema,
    RoleSchema,
)

role_router = APIRouter()


@role_router.post(
    "/add",
    response_model=RoleResponseSchema,
    summary="Добавление новой роли",
    status_code=status.HTTP_201_CREATED,
)
async def add_role(
    data: RoleCreateSchema = Body(...), _: dict = Depends(require_superadmin)
):
    logger.info(f"Создание роли: {data.model_dump()}")
    try:
        role = await Role.create(name=data.name, application_id=data.application_id)
        logger.success(f"Роль {role.name} ({role.id}) успешно создана")
        return {"role_id": role.id}
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@role_router.post(
    "/add-many",
    response_model=RoleResponseSchema,
    summary="Добавление новой роли",
    status_code=status.HTTP_201_CREATED,
)
async def add_many_roles(
    data: RoleCreateManySchema = Body(...),
    _: dict = Depends(require_superadmin),
):
    logger.info(f"Создание роли: {data.model_dump()}")
    try:
        role = await Role.create(name=data.name, application_id=data.application_id)
        await RolePermissionRelation.bulk_create(
            [
                RolePermissionRelation(role_id=role.id, permission_id=permission_id)
                for permission_id in data.permissions
            ]
        )
        logger.success(f"Роль {role.name} ({role.id}) успешно создана")
        return {"role_id": role.id}
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@role_router.patch(
    "/{role_id}", response_model=RoleResponseSchema, summary="Изменение роли"
)
async def edit_role(
    role_id: UUID = Path(..., title="ID роли", description="ID изменяемой роли"),
    data: RoleEditSchema = Body(...),
    _: dict = Depends(require_superadmin),
):
    logger.info(f"Обновление роли {role_id}: {data.model_dump(exclude_unset=True)}")
    try:
        role = await Role.filter(id=role_id).first()
        if not role:
            logger.warning(f"Роль {role_id} не найдена")
            raise HTTPException(status_code=404, detail="Роль не найдена")

        if role.system_name:
            raise HTTPException(
                status_code=403, detail="Нельзя изменить системную роль"
            )

        await role.update_from_dict(data.model_dump(exclude_unset=True))
        await role.save()

        logger.success(f"Роль {role_id} успешно обновлена")
        return RoleResponseSchema(role_id=role.id)
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@role_router.delete(
    "/{role_id}", summary="Удаление роли", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_role(
    role_id: UUID = Path(..., title="ID роли", description="ID удаляемой роли"),
    _: dict = Depends(require_superadmin),
):
    logger.info(f"Удаление роли {role_id}")
    try:
        role = await Role.filter(id=role_id).first()
        if not role:
            logger.warning(f"Роль {role_id} не найдена")
            raise HTTPException(status_code=404, detail="Роль не найдена")

        if role.system_name:
            raise HTTPException(status_code=403, detail="Нельзя удалить системную роль")

        await role.delete()

        logger.success(f"Роль {role_id} успешно удалена")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@role_router.get(
    "/all",
    response_model=RoleListResponseSchema,
    summary="Получение списка ролей с фильтрацией",
)
async def get_roles(
    filters: RoleFilterSchema = Depends(),
    _: dict = Depends(get_current_user),
):
    logger.info(f"Запрос на список ролей: {filters.model_dump()}")

    query = Q()
    if filters.role_name:
        query &= Q(name__icontains=filters.role_name)
    if filters.application_id:
        query &= Q(application_id=filters.application_id)

    if filters.order not in ("asc", "desc"):
        raise HTTPException(
            status_code=422, detail="order должен быть 'asc' или 'desc'"
        )

    sort_field = filters.sort_by if filters.order == "asc" else f"-{filters.sort_by}"

    total_count = await Role.filter(query).count()

    roles_raw = (
        await Role.filter(query)
        .order_by(sort_field)
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
        .values("id", "name", "system_name", "application_id")
    )

    roles = [RoleSchema(**role) for role in roles_raw]

    return RoleListResponseSchema(total=total_count, roles=roles)


@role_router.get("/{role_id}", response_model=RoleSchema, summary="Просмотр роли")
async def get_role(
    role_id: UUID = Path(..., title="ID роли", description="ID просматриваемой роли"),
    _: str = Depends(get_current_user),
):
    logger.info(f"Запрос на просмотр роли: {role_id}")

    role_raw = (
        await Role.filter(id=role_id)
        .first()
        .values("id", "name", "system_name", "application_id")
    )

    if not role_raw:
        logger.warning(f"Роль {role_id} не найдена")
        raise HTTPException(status_code=404, detail="Роль не найдена")

    role_schema = RoleSchema(**role_raw)
    logger.success(f"Роль найдена: {role_schema}")
    return role_schema
