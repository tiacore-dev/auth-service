from uuid import UUID

import bcrypt
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from tortoise.expressions import Q

from app.database.models import Company, Role, User, UserCompanyRelation, create_user
from app.dependencies.permissions import with_permission_and_company_check
from app.handlers.auth import require_superadmin
from app.handlers.depends import (
    require_permission_in_context,
    require_permission_or_self_view,
)
from app.pydantic_models.user_models import (
    UserCreateSchema,
    UserEditSchema,
    UserListResponseSchema,
    UserResponseSchema,
    UserSchema,
    user_filter_params,
)

user_router = APIRouter()


@user_router.post(
    "/add",
    response_model=UserResponseSchema,
    summary="Добавление нового пользователя",
    status_code=status.HTTP_201_CREATED,
)
async def add_user(data: UserCreateSchema = Body(...), _=Depends(require_superadmin)):
    logger.info(f"Создание пользователя: {data.email}")
    try:
        existing_user = await User.get_or_none(email=data.email)
        if existing_user:
            logger.warning(f"Пользователь с логином {data.email} уже существует")
            raise HTTPException(status_code=400, detail="Имя пользователя занято")
        logger.debug(f"Попытка создать пользователя {data.email}")
        user = await create_user(
            email=data.email,
            full_name=data.full_name,
            position=data.position,
            password=data.password,
        )
        logger.debug(f"Пользователь создан: {user.id}")
        if not user:
            logger.error("Не удалось создать пользователя")
            raise HTTPException(
                status_code=500, detail="Не удалось создать пользователя"
            )
        logger.success(f"Пользователь {user.email} ({user.id}) успешно создан")
        role = await Role.get_or_none(
            system_name="user", application_id=data.application_id
        )
        company = await Company.get_or_none(id=data.company_id)
        if role and company:
            await UserCompanyRelation.create(user=user, company=company, role=role)
        return {"user_id": str(user.id)}
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@user_router.patch(
    "/{user_id}", response_model=UserResponseSchema, summary="Изменение пользователя"
)
async def edit_user(
    user_id: UUID,
    data: UserEditSchema = Body(...),
    context=with_permission_and_company_check("edit_user"),
):
    logger.info(f"Обновление пользователя {user_id}: {data.email}")

    update_data = data.model_dump(exclude_unset=True)

    if "password" in update_data:  # Если передан пароль, хешируем его
        update_data["password_hash"] = bcrypt.hashpw(
            update_data.pop("password").encode(), bcrypt.gensalt()
        ).decode()
    if "is_verified" in update_data:
        if not context["is_superadmin"]:
            update_data.pop("is_verified")
    updated_rows = None
    if update_data:
        updated_rows = await User.filter(id=user_id).update(**update_data)

    if not updated_rows:
        logger.warning(f"Пользователь {user_id} не найден")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    logger.success(f"Пользователь {user_id} успешно обновлён")
    return {"user_id": str(user_id)}


@user_router.delete(
    "/{user_id}",
    summary="Удаление пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID, _=with_permission_and_company_check("delete_user")
):
    logger.info(f"Удаление пользователя {user_id}")
    try:
        user = await User.filter(id=user_id).first()
        if not user:
            logger.warning(f"Пользователь {user_id} не найден")
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if user.email == "admin":
            raise HTTPException(
                status_code=403, detail="вы не можете удалить администратора."
            )
        await user.delete()
        logger.success(f"Пользователь {user_id} успешно удален")
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@user_router.get(
    "/all", response_model=UserListResponseSchema, summary="Просмотр пользователей"
)
async def get_users(
    filters: dict = Depends(user_filter_params),
    context=Depends(require_permission_in_context("get_all_users")),
):
    query = Q()
    search_value = filters.get("search")
    if search_value:
        query &= Q(email__icontains=search_value)

    company_filter = filters.get("company")

    if context["is_superadmin"]:
        if company_filter:
            related_user_ids = await UserCompanyRelation.filter(
                company=company_filter
            ).values_list("user_id", flat=True)

            if related_user_ids:
                query &= Q(id__in=related_user_ids)
            else:
                return UserListResponseSchema(total=0, users=[])
    else:
        if not context.get("company"):
            logger.info(f"Нет компании в контексте для пользователя {context['user']}")
            return UserListResponseSchema(total=0, users=[])

        related_user_ids = await UserCompanyRelation.filter(
            company=context["company"]
        ).values_list("user_id", flat=True)

        if related_user_ids:
            query &= Q(id__in=related_user_ids)
        else:
            return UserListResponseSchema(total=0, users=[])

    order = filters.get("order", "asc")
    sort_by = filters.get("sort_by", "email")
    order_by = f"{'-' if order == 'desc' else ''}{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await User.filter(query).count()

    users = (
        await User.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    users_data = [
        UserSchema(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            position=user.position,
            is_verified=user.is_verified,
        )
        for user in users
    ]

    return UserListResponseSchema(total=total_count, users=users_data)


@user_router.get(
    "/{user_id}", response_model=UserSchema, summary="Просмотр пользователя"
)
async def get_user(
    user_id: UUID = Path(
        ..., title="ID пользователя", description="ID просматриваемого пользователя"
    ),
    context: dict = Depends(require_permission_or_self_view("view_user")),
):
    logger.info(f"Получен запрос на просмотр пользователя: {user_id}")

    user = await User.get_or_none(id=user_id)
    if user is None:
        logger.warning(f"Пользователь {user_id} не найден")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # 🔐 Проверка доступа
    if not context["is_superadmin"]:
        # Получаем список user_id в рамках текущей компании
        allowed_user_ids = await UserCompanyRelation.filter(
            company=context["company"]
        ).values_list("user_id", flat=True)

        if user_id not in allowed_user_ids:
            raise HTTPException(
                status_code=403, detail="Нет доступа к этому пользователю"
            )

    return UserSchema(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        position=user.position,
        is_verified=user.is_verified,
    )
