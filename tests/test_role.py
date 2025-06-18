import pytest
from httpx import AsyncClient

from app.database.models import Role


@pytest.mark.asyncio
async def test_add_role(test_app: AsyncClient, jwt_token_admin: dict):
    """Тест добавления новой роли."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"role_name": "Test Role", "application_id": "test_app"}

    response = await test_app.post("/api/roles/add", headers=headers, json=data)
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    role = await Role.filter(name="Test Role").first()

    assert role is not None, "Роль не была сохранена в БД"
    assert response_data["role_id"] == str(role.id)


@pytest.mark.asyncio
async def test_edit_role(
    test_app: AsyncClient, jwt_token_admin: dict, other_role: Role
):
    """Тест редактирования роли."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"role_name": "Updated Role Name"}

    response = await test_app.patch(
        f"/api/roles/{other_role.id}", headers=headers, json=data
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    role = await Role.filter(id=other_role.id).first()

    assert role is not None, "Роль не найдена в БД"
    assert response_data["role_id"] == str(role.id)
    assert role.name == "Updated Role Name"


@pytest.mark.asyncio
async def test_view_role(
    test_app: AsyncClient, jwt_token_admin: dict, other_role: Role
):
    """Тест просмотра роли по ID."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/roles/{other_role.id}", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    assert response_data["role_id"] == str(other_role.id)
    assert response_data["role_name"] == other_role.name


@pytest.mark.asyncio
async def test_delete_role(
    test_app: AsyncClient, jwt_token_admin: dict, other_role: Role
):
    """Тест удаления роли."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(f"/api/roles/{other_role.id}", headers=headers)

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    role = await Role.filter(id=other_role.id).first()
    assert role is None, "Роль не была удалена из БД"


@pytest.mark.asyncio
async def test_get_roles(
    test_app: AsyncClient, jwt_token_admin: dict, other_role: Role
):
    """Тест получения списка ролей с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/roles/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    roles = response_data.get("roles")
    assert isinstance(roles, list), "Ответ должен быть списком"
    assert response_data.get("total") > 0

    role_ids = [role["role_id"] for role in roles]
    assert str(other_role.id) in role_ids, "Тестовая роль отсутствует в списке"
