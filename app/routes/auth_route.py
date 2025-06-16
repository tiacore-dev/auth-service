from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from jose import JWTError
from loguru import logger
from tiacore_lib.config import get_settings
from tiacore_lib.pydantic_models.auth_models import (
    LoginRequest,
    MEResponse,
    RefreshRequest,
    TokenResponse,
    UserCompanyRelationOut,
)
from tiacore_lib.rabbit.models import EventType, UserEvent

from app.database.models import User, UserCompanyRelation
from app.handlers.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    login_handler,
    verify_token,
)
from app.utils.event_builder import build_user_event
from app.utils.permissions_get import (
    get_company_permissions_by_application,
    get_company_permissions_for_user,
)

auth_router = APIRouter()


@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, request: Request, settings=Depends(get_settings)):
    result = await login_handler(data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    try:
        user, company_permissions = result
        logger.debug(f"Полученные разрешения: {company_permissions}")
        event = await build_user_event(user, event_type=EventType.USER_LOGGED_IN)
        await request.app.state.publisher.publish_event(event)

        return TokenResponse(
            access_token=create_access_token({"sub": user.email}, settings),
            refresh_token=create_refresh_token({"sub": user.email}, settings),
            permissions=None if user.is_superadmin else company_permissions,
            is_superadmin=user.is_superadmin,
            user_id=user.id,
        )
    except Exception as e:
        logger.exception("🔥 Ошибка при авторизации")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@auth_router.post(
    "/refresh", response_model=TokenResponse, summary="Обновление Access Token"
)
async def refresh_access_token(data: RefreshRequest, settings=Depends(get_settings)):
    try:
        logger.debug("Запрос на рефреш токена")
        refresh_token = data.refresh_token
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")

        payload = await verify_token(refresh_token, settings)
        email = payload["email"]

        user = await User.get_or_none(email=email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        company_permissions = await get_company_permissions_for_user(user)
        logger.debug(f"🧪 is_superadmin: {user.is_superadmin}")
        logger.debug(f"🧪 permissions: {company_permissions}")

        return TokenResponse(
            access_token=create_access_token({"sub": email}, settings),
            refresh_token=create_refresh_token({"sub": email}, settings),
            permissions=None if user.is_superadmin else company_permissions,
            is_superadmin=user.is_superadmin,
            user_id=user.id,
        )

    except JWTError as exc:
        raise HTTPException(
            status_code=401, detail="Неверный или просроченный токен"
        ) from exc


@auth_router.get(
    "/me", response_model=MEResponse, summary="Получение инфы о пользователе"
)
async def give_user_data(
    application_id: str = Query(...), token_data=Depends(get_current_user)
):
    user = await User.get_or_none(id=token_data["user_id"])
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token data")
    relations = (
        await UserCompanyRelation.filter(user=user)
        .prefetch_related("company", "role")
        .all()
    )
    relation_list = [
        UserCompanyRelationOut(
            id=str(r.id), company_id=str(r.company.id), role=r.role.name
        )
        for r in relations
    ]

    company_list = [relation.company.id for relation in relations]
    permissions = await get_company_permissions_by_application(user, application_id)

    return MEResponse(
        user_id=user.id,
        is_superadmin=user.is_superadmin,
        email=user.email,
        permissions=permissions,
        companies=company_list,
        relations=relation_list,
    )


@auth_router.post("/logout", summary="Логаут")
async def logout(
    request: Request,
    token_data=Depends(get_current_user),
):
    logger.info(f"Пользователь {token_data['email']} вышел из системы")
    event = UserEvent(
        event=EventType.USER_LOGGED_OUT,
        email=token_data["email"],
    )
    await request.app.state.publisher.publish_event(event)
