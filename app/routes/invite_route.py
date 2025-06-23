from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from tiacore_lib.config import get_settings
from tiacore_lib.pydantic_models.auth_models import (
    InviteRequest,
    RegisterRequest,
    TokenResponse,
)
from tiacore_lib.utils.verification import send_email

from app.config import get_front_url
from app.database.models import (
    Application,
    Company,
    User,
    UserCompanyRelation,
    create_user,
)
from app.handlers.auth import (
    create_access_token,
    create_refresh_token,
    generate_token,
    get_current_user,
    verify_jwt_token,
)
from app.utils.permissions_get import get_company_permissions_for_user

invite_router = APIRouter()


@invite_router.post("/invite", status_code=201)
async def invite_user(
    data: InviteRequest, _=Depends(get_current_user), settings=Depends(get_settings)
):
    payload = {
        "sub": data.email,
        "company_id": str(data.company_id),
        "role_id": str(data.role_id),
        "application_id": data.application_id,
    }
    token = generate_token(payload, settings)
    application = await Application.get_or_none(id=data.application_id)
    if not application:
        raise HTTPException(
            status_code=400, detail="Попытка пригласить в несуществующее приложение"
        )
    existing_user = await User.get_or_none(email=data.email)
    front_url = get_front_url(application_id=application.id, settings=settings)
    if existing_user:
        verification_link = f"{front_url}/accept-invite?token={token}"
        company = await Company.get_or_none(company_id=data.company_id)
        if not company:
            raise HTTPException(status_code=400, detail="Компания не найдена")
        body = f"""
        Здравствуйте!

        Вас пригласили в компанию: {company.name} внутри {application.name}. 
        Для подтверждения перейдите по ссылке:

        {verification_link}

        Если вас пригласили по ошибке, проигнорируйте это письмо.
        """
        await send_email(data.email, body, settings)
        return

    verification_link = f"{front_url}/invite?token={token}&email={data.email}"
    body = f"""
    Здравствуйте!

    Вас пригласили в {application.name}. Для регистрации перейдите по ссылке:

    {verification_link}

    """
    await send_email(data.email, body, settings)
    return


@invite_router.post(
    "/register-with-token", response_model=TokenResponse, status_code=201
)
async def register_with_token(
    data: RegisterRequest,
    token: str = Query(...),
    settings=Depends(get_settings),
):
    user = await create_user(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        position=data.position,
    )
    user.is_verified = True
    await user.save()

    token_data = verify_jwt_token(token, settings)
    company_id = token_data.get("company_id")
    role_id = token_data.get("role_id")
    application_id = token_data.get("application_id")
    if not company_id or not role_id:
        raise HTTPException(status_code=400, detail="Invalid invitation token")
    existing_relation = await UserCompanyRelation.exists(
        user=user, company_id=company_id, role_id=role_id, application_id=application_id
    )

    if existing_relation:
        logger.info("🔁 Связь уже существует")
    else:
        await UserCompanyRelation.create(
            user=user,
            company_id=company_id,
            role_id=role_id,
            application_id=application_id,
        )
    return TokenResponse(
        access_token=create_access_token({"sub": user.email}, settings),
        refresh_token=create_refresh_token({"sub": user.email}, settings),
        permissions=None
        if user.is_superadmin
        else await get_company_permissions_for_user(user),
        is_superadmin=user.is_superadmin,
        user_id=user.id,
    )


@invite_router.get("/accept-invite", status_code=201)
async def accept_invite(token: str = Query(...), settings=Depends(get_settings)):
    logger.info(f"Получен токен: {token}")
    token_data = verify_jwt_token(token, settings)
    company_id = token_data.get("company_id")
    role_id = token_data.get("role_id")
    application_id = token_data.get("application_id")
    email = token_data.get("sub")
    user = await User.get_or_none(email=email)
    if not company_id or not role_id or not user:
        raise HTTPException(status_code=400, detail="Invalid invitation token")
    existing_relation = await UserCompanyRelation.exists(
        user=user, company_id=company_id, role_id=role_id, application_id=application_id
    )

    if existing_relation:
        logger.info("🔁 Связь уже существует")
        return
    await UserCompanyRelation.create(user=user, company_id=company_id, role_id=role_id)
    return
