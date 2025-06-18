import pytest
from httpx import AsyncClient

from app.database.models import Company, User, UserCompanyRelation


@pytest.mark.asyncio
async def test_add_user(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_company: Company,
    user_role,
    seed_application,
):
    """Тест добавления нового пользователя."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "email": "testuser",
        "full_name": "Test User",
        "position": "Developer",
        "password": "securepassword123",
        "company_id": str(seed_company.id),
        "application_id": str(seed_application.id),
    }

    response = await test_app.post("/api/users/add", headers=headers, json=data)
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    # Проверяем, что пользователь добавлен в базу
    response_data = response.json()
    user = await User.filter(email="testuser").first()
    relation = (
        await UserCompanyRelation.filter(user=user)
        .prefetch_related("company", "role")
        .first()
    )
    if not relation:
        raise AssertionError("Связь с компанией не найдена")
    assert user is not None, "Пользователь не был сохранён в БД"
    assert relation.role.id == user_role.id
    assert response_data["user_id"] == str(user.id)

    assert str(relation.company.id) == str(seed_company.id)


@pytest.mark.asyncio
async def test_edit_user(
    test_app: AsyncClient, jwt_token_admin, seed_user: User, seed_company: Company
):
    """Тест редактирования пользователя."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"full_name": "Updated User", "position": "Senior Developer"}

    response = await test_app.patch(
        f"/api/users/{seed_user.id}?company={seed_company.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    # Проверяем, что пользователь обновился в базе
    response_data = response.json()
    user = await User.filter(id=seed_user.id).first()

    assert user is not None, "Пользователь не найден в базе"
    assert response_data["user_id"] == str(user.id)
    assert user.full_name == "Updated User"
    assert user.position == "Senior Developer"


@pytest.mark.asyncio
async def test_delete_user(
    test_app: AsyncClient, jwt_token_admin, seed_user: User, seed_company: Company
):
    """Тест удаления пользователя."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/users/{seed_user.id}?company={seed_company.id}",
        headers=headers,
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    user = await User.filter(id=seed_user.id).first()
    assert user is None, "Пользователь не был удалён из базы"


@pytest.mark.asyncio
async def test_get_users(test_app: AsyncClient, jwt_token_admin, seed_user: User):
    """Тест получения списка пользователей с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/users/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    users = response_data.get("users")
    assert isinstance(users, list), "Ответ должен быть списком"

    # Проверяем, что в списке есть наш тестовый пользователь
    user_ids = [user["user_id"] for user in users]
    assert str(seed_user.id) in user_ids, "Тестовый пользователь отсутствует в списке"


@pytest.mark.asyncio
async def test_view_user(test_app: AsyncClient, jwt_token_admin: dict, seed_user: User):
    """Тест просмотра пользователя по ID."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/users/{seed_user.id}", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    print(response_data)  # Посмотрим, какие поля реально пришли

    assert response_data["user_id"] == str(seed_user.id)
    assert response_data["email"] == seed_user.email
    assert response_data["full_name"] == seed_user.full_name
