import pytest
from httpx import AsyncClient

from app.database.models import Application, User

# @pytest.mark.usefixtures("seed_other_user")
# @pytest.mark.asyncio
# async def test_login_success(test_app: AsyncClient):
#     """Проверяем успешную аутентификацию."""
#     response = await test_app.post(
#         "/api/auth/login",
#         json={
#             "email": "Test User",
#             "password": "123",
#         },
#     )

#     assert response.status_code == 200
#     json_data = response.json()
#     assert "access_token" in json_data
#     assert "refresh_token" in json_data


@pytest.mark.asyncio
async def test_refresh_token_success(test_app: AsyncClient, jwt_token_admin, seed_application: Application):
    """Проверяем, что refresh-токен можно обменять на новый access-токен."""
    response = await test_app.post(
        "/api/auth/refresh",
        json={
            "refresh_token": jwt_token_admin["refresh_token"],
            "application_id": seed_application.id,
        },
    )

    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data


@pytest.mark.asyncio
async def test_login_failure(test_app: AsyncClient, seed_application: Application, seed_user: User):
    """Проверяем неудачную аутентификацию с неправильным паролем."""
    response = await test_app.post(
        "/api/auth/login",
        json={
            "email": seed_user.email,
            "password": "wrongpassword",
            "application_id": seed_application.id,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == f"Неверный пароль для пользователя '{seed_user.email}'"


@pytest.mark.asyncio
async def test_refresh_token_invalid(test_app, seed_application: Application):
    """Проверяем обновление токена с неверным refresh-токеном."""
    response = await test_app.post(
        "/api/auth/refresh",
        json={"refresh_token": "invalid token", "application_id": seed_application.id},
    )

    assert response.status_code == 401
