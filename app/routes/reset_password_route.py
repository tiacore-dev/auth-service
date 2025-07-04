from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from tiacore_lib.config import get_settings
from tiacore_lib.pydantic_models.auth_models import ResetPasswordRequest, VerifyReset
from tiacore_lib.utils.verification import send_email

from app.config import get_front_url
from app.database.models import (
    User,
)
from app.handlers.auth import (
    generate_token,
    verify_jwt_token,
)

reset_router = APIRouter()


@reset_router.post("/reset-password", status_code=201)
async def reset_password(data: ResetPasswordRequest, settings=Depends(get_settings)):
    payload = {
        "sub": data.email,
        "application_id": data.application_id,
    }
    token = generate_token(payload, settings)
    front_url = get_front_url(application_id=data.application_id, settings=settings)

    verification_link = f"{front_url}/reset-password?token={token}"
    body = f"""
    Здравствуйте!

    Мы получили запрос об изменении пароля. Чтобы сбросить пароль, перейдите по ссылке:

    {verification_link}

    Если это были не вы, можете проигнорировать это письмо.

    """
    await send_email(data.email, body, settings)
    return


@reset_router.post("/reset-verify", status_code=201)
async def reset_verify(
    data: VerifyReset, token: str = Query(...), settings=Depends(get_settings)
):
    logger.info(f"Получен токен: {token}")
    token_data = verify_jwt_token(token, settings)
    email = token_data.get("sub")
    user = await User.get_or_none(email=email)
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    user.update_password(password=data.password)
    await user.save()
    return
