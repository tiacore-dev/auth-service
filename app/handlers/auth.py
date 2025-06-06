from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from loguru import logger
from tiacore_lib.config import get_settings

from app.auth_schemas import bearer_scheme
from app.database.models import User
from app.utils.permissions_get import get_company_permissions_for_user

# Конфигурация JWT


def generate_token(payload: dict, settings, expires_in_hours: int = 1) -> str:
    payload = {
        **payload,
        "exp": datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def verify_jwt_token(token: str, settings) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"❌ Ошибка при декодировании токена: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token") from e


def create_access_token(data: dict, settings, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# Проверка токена


def create_refresh_token(data: dict, settings):
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(data, settings=settings, expires_delta=expires)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    settings=Depends(get_settings),
) -> dict:
    if (
        not credentials
        or not credentials.credentials
        or credentials.credentials.strip() == ""
    ):
        logger.warning("❌ Отсутствует или пустой токен Authorization")
        raise HTTPException(status_code=401, detail="Missing or empty token")

    token = credentials.credentials.strip()

    token_data = await verify_token(token, settings)
    return token_data


async def verify_token(token: str, settings) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            logger.warning("❌ Токен не содержит 'sub'. Отказ в доступе.")
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await User.get_or_none(email=email)
        if not user:
            logger.warning(
                "❌ Пользователь или application не найдены. Отказ в доступе."
            )
            raise HTTPException(
                status_code=401, detail="Invalid token or missing application"
            )
        permissions = await get_company_permissions_for_user(user)
        token_data = {
            "email": email,
            "permissions": permissions,
            "is_superadmin": user.is_superadmin,
            "user_id": str(user.id),
        }

        return token_data

    except JWTError as e:
        logger.warning(f"❌ Ошибка при декодировании токена: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token") from e


async def login_handler(email: str, password: str):
    user = await User.get_or_none(email=email)

    if not user:
        logger.warning(f"🔐 Пользователь '{email}' не найден")
        return None

    if not user.check_password(password):
        logger.warning(f"🔐 Неверный пароль для пользователя '{email}'")
        return None

    if not user.is_verified and not user.is_superadmin:
        raise HTTPException(status_code=403, detail="Необходимо верифицировать email")

    company_permissions = await get_company_permissions_for_user(user)

    return user, company_permissions


async def require_superadmin(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    settings=Depends(get_settings),
) -> dict:
    if not credentials or not credentials.credentials.strip():
        logger.warning("❌ Отсутствует или пустой токен Authorization")
        raise HTTPException(status_code=401, detail="Missing or empty token")

    token = credentials.credentials.strip()
    user_data = await verify_token(token, settings)

    email = user_data.get("email")
    if not email:
        logger.warning("❌ Токен не содержит имя пользователя")
        raise HTTPException(status_code=401, detail="Invalid token")

    if not user_data["is_superadmin"]:
        logger.warning(f"🚫 Пользователь {email} не является суперадмином")
        raise HTTPException(status_code=403, detail="Только для суперадминов")

    logger.info(f"✅ Суперадмин авторизован: {email}")
    return {
        "user": user_data["user_id"],
        "email": email,
        "is_superadmin": True,
    }
