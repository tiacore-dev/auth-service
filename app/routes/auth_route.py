from fastapi import APIRouter, Depends, HTTPException, Query, Request
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
from app.handlers.cache_handler import blacklist_token
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

    user, company_permissions = result
    logger.debug(f"Полученные разрешения: {company_permissions}")
    event = await build_user_event(user, event_type=EventType.USER_LOGGED_IN)
    await request.app.state.publisher.publish_event(event)

    return TokenResponse(
        access_token=create_access_token({"sub": user.email}, settings, type="access"),
        refresh_token=create_refresh_token({"sub": user.email}, settings, type="refresh"),
        permissions=None if user.is_superadmin else company_permissions,
        is_superadmin=user.is_superadmin,
        user_id=user.id,
    )


@auth_router.post("/refresh", response_model=TokenResponse, summary="Обновление Access Token")
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

        return TokenResponse(
            access_token=create_access_token({"sub": user.email}, settings, type="access"),
            refresh_token=create_refresh_token({"sub": user.email}, settings, type="refresh"),
            permissions=None if user.is_superadmin else company_permissions,
            is_superadmin=user.is_superadmin,
            user_id=user.id,
        )

    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Неверный или просроченный токен") from exc


@auth_router.get("/me", response_model=MEResponse, summary="Получение инфы о пользователе")
async def give_user_data(
    application_id: str = Query(..., description="UUID приложения (строкой)"),
    token_data=Depends(get_current_user),
):
    logger.debug(f"[auth.me] start: application_id={application_id!s} user_id={token_data.get('user_id')}")

    user = await User.get_or_none(id=token_data["user_id"])
    if not user:
        logger.warning("[auth.me] invalid token: user not found")
        raise HTTPException(status_code=400, detail="Invalid token data")

    # --- Relations
    relations = await UserCompanyRelation.filter(user=user).prefetch_related("company", "role").all()
    rel_preview = [
        {
            "rel_id": str(r.id),
            "company_id": str(getattr(r, "company_id", getattr(r.company, "id", None))),
            "role": getattr(r.role, "system_name", getattr(r.role, "name", None)),
            # Если у модели есть поле application_id — полезно увидеть его тоже:
            "application_id": str(getattr(r, "application_id", "")) or None,
        }
        for r in relations[:3]
    ]
    logger.debug(f"[auth.me] relations: count={len(relations)} preview={rel_preview}")

    relation_list = [
        UserCompanyRelationOut(
            id=str(r.id),
            company_id=str(getattr(r, "company_id", r.company.id)),
            role=getattr(r.role, "name", None),
        )
        for r in relations
    ]
    company_list = [str(getattr(r, "company_id", r.company.id)) for r in relations]

    logger.debug(f"[auth.me] companies: count={len(company_list)} sample={company_list[:5]}")

    # --- Permissions (как возвращает get_company_permissions_by_application)
    permissions = await get_company_permissions_by_application(user, application_id)
    if isinstance(permissions, dict):
        logger.debug(f"[auth.me] raw permissions: type=dict keys(top5)={list(permissions.keys())[:5]}")
    else:
        logger.debug(f"[auth.me] raw permissions: type={type(permissions).__name__} preview={str(permissions)[:200]}")

    # Если permissions в формате {app_id: {company_id: [perm,...]}}
    if permissions:
        filtered_permissions = permissions.get(application_id, {})
    else:
        filtered_permissions = {}

    if isinstance(filtered_permissions, dict):
        perm_company_keys = list(filtered_permissions.keys())
        logger.debug(
            f"[auth.me] filtered_permissions: companies={len(perm_company_keys)} keys(top5)={perm_company_keys[:5]}"
        )
        if perm_company_keys:
            first_key = perm_company_keys[0]
            first_val = filtered_permissions.get(first_key) or []
            logger.debug(f"[auth.me] first company={first_key} perms(sample)={first_val[:10]}")
    else:
        logger.debug(f"[auth.me] filtered_permissions: type={type(filtered_permissions).__name__}")

    response = MEResponse(
        user_id=user.id,
        is_superadmin=user.is_superadmin,
        email=user.email,
        permissions=filtered_permissions,
        companies=company_list,
        relations=relation_list,
    )

    try:
        # model_dump доступен в Pydantic v2; если v1 — замените на .dict()
        payload = response.model_dump()
    except Exception:
        payload = response.dict()

    logger.debug(
        "[auth.me] response summary: keys=%s companies=%s perms_companies=%s",
        list(payload.keys()),
        len(payload.get("companies") or []),
        len((payload.get("permissions") or {}) if isinstance(payload.get("permissions"), dict) else []),
    )

    return response


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
    await blacklist_token(token_data["jti"])
    await request.app.state.publisher.publish_event(event)
