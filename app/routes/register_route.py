from fastapi import APIRouter, Body, HTTPException, Query
from loguru import logger

from app.config import get_settings
from app.database.models import User, create_user
from app.handlers.auth import (
    generate_token,
    verify_jwt_token,
)
from app.pydantic_models.auth_models import (
    RegisterRequest,
    RegisterResponse,
)
from app.utils.verification import send_email

settings = get_settings()


register_router = APIRouter()


@register_router.post("/register", response_model=RegisterResponse)
async def register(data: RegisterRequest):
    user = await create_user(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        position=data.position,
    )
    token = generate_token({"sub": str(user.id), "application": data.application_id})
    logger.info(f"Пользователь зарегистрирован: {user.email}, user_id={user.id}")
    verification_link = f"{settings.FRONT_ORIGIN}/login?token={token}"
    body = f"""
    Здравствуйте!

    Пожалуйста, подтвердите свою почту, перейдя по ссылке:
    {verification_link}

    Если это были не вы, проигнорируйте это письмо.
    """
    await send_email(user.email, body)
    return RegisterResponse(user_id=user.id)


@register_router.post("/resend-verification")
async def resend_verification(
    email: str = Body(..., embed=True), application_id: str = Body(..., embed=True)
):
    user = await User.get_or_none(email=email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_verified:
        return {"message": "Почта уже подтверждена"}

    token = generate_token({"sub": str(user.id)})
    verification_link = f"{settings.FRONT_ORIGIN}/login?token={token}"
    body = f"""
    Здравствуйте!

    Для подтверждения почты перейдите по ссылке:
    {verification_link}

    Если вы не регистрировались, проигнорируйте это письмо.
    """
    await send_email(user.email, body)
    logger.info(f"Письмо с подтверждением повторно отправлено: {user.email}")
    return {"message": "Письмо отправлено повторно"}


@register_router.get("/verify-email")
async def verify_email(token: str = Query(...)):
    payload = verify_jwt_token(token)
    user_id = payload.get("sub")
    if not user_id:
        logger.warning(f"Попытка верификации с некорректным токеном: {token}")
        raise HTTPException(status_code=400, detail="Проблема с токеном")

    user = await User.get_or_none(id=user_id)
    if not user:
        logger.warning(
            f"Пользователь не найден при верификации почты, user_id={user_id}"
        )
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    if user.is_verified:
        logger.info(f"Почта уже подтверждена ранее, user_id={user.id}")
        return {"message": "Почта уже подтверждена"}

    user.is_verified = True
    await user.save()

    logger.info(f"Почта успешно подтверждена, user_id={user.id}")
    return {"message": "Почта успешно подтверждена!"}
