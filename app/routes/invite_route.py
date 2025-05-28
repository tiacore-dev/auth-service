from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from app.config import get_settings
from app.database.models import Company, User, UserCompanyRelation, create_user
from app.handlers.auth import (
    create_access_token,
    create_refresh_token,
    generate_token,
    get_current_user,
    verify_jwt_token,
)
from app.pydantic_models.auth_models import (
    InviteRequest,
    RegisterRequest,
    TokenResponse,
)
from app.utils.permissions_get import get_company_permissions_for_user
from app.utils.verification import send_email

settings = get_settings()

invite_router = APIRouter()


@invite_router.post("/invite", status_code=201)
async def invite_user(data: InviteRequest, _=Depends(get_current_user)):
    payload = {
        "sub": data.email,
        "company_id": str(data.company_id),
        "role_id": str(data.role_id),
    }
    token = generate_token(payload)

    existing_user = await User.get_or_none(email=data.email)
    if existing_user:
        verification_link = f"{settings.FRONT_ORIGIN}/accept-invite?token={token}"
        company = await Company.get_or_none(company_id=data.company_id)
        if not company:
            raise HTTPException(status_code=400, detail="Компания не найдена")
        body = f"""
        Здравствуйте!

        Вас пригласили в компанию: {company.name} внутри Tiacore CRM. 
        Для подтверждения перейдите по ссылке:

        {verification_link}

        Если вас пригласили по ошибке, проигнорируйте это письмо.
        """
        await send_email(data.email, body)
        return

    verification_link = (
        f"{settings.FRONT_ORIGIN}/invite?token={token}&email={data.email}"
    )
    body = f"""
    Здравствуйте!

    Вас пригласили в Tiacore CRM. Для регистрации перейдите по ссылке:

    {verification_link}

    """
    await send_email(data.email, body)
    return


@invite_router.post(
    "/register-with-token", response_model=TokenResponse, status_code=201
)
async def register_with_token(data: RegisterRequest, token: str = Query(...)):
    user = await create_user(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        position=data.position,
    )
    user.is_verified = True
    await user.save()

    token_data = verify_jwt_token(token)
    company_id = token_data.get("company_id")
    role_id = token_data.get("role_id")
    if not company_id or not role_id:
        raise HTTPException(status_code=400, detail="Invalid invitation token")
    existing_relation = await UserCompanyRelation.exists(
        user=user, company_id=company_id, role_id=role_id
    )

    if existing_relation:
        logger.info("🔁 Связь уже существует")
    else:
        await UserCompanyRelation.create(
            user=user, company_id=company_id, role_id=role_id
        )
    return TokenResponse(
        access_token=create_access_token(
            {"sub": user.email, "user_id": user.id, "application": data.application_id}
        ),
        refresh_token=create_refresh_token(
            {"sub": user.email, "user_id": user.id, "application": data.application_id}
        ),
        permissions=None
        if user.is_superadmin
        else await get_company_permissions_for_user(user, data.application_id),
        is_superadmin=user.is_superadmin,
        user_id=user.id,
    )


@invite_router.get("/accept-invite", status_code=201)
async def accept_invite(token: str = Query(...)):
    logger.info(f"Получен токен: {token}")
    token_data = verify_jwt_token(token)
    company_id = token_data.get("company_id")
    role_id = token_data.get("role_id")
    email = token_data.get("sub")
    user = await User.get_or_none(email=email)
    if not company_id or not role_id or not user:
        raise HTTPException(status_code=400, detail="Invalid invitation token")
    existing_relation = await UserCompanyRelation.exists(
        user=user, company_id=company_id, role_id=role_id
    )

    if existing_relation:
        logger.info("🔁 Связь уже существует")
        return
    await UserCompanyRelation.create(user=user, company_id=company_id, role_id=role_id)
    return
