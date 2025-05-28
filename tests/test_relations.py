import pytest
from httpx import AsyncClient

from app.database.models import Company, Role, User, UserCompanyRelation


@pytest.mark.asyncio
async def test_add_user_company_relation(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_user: User,
    seed_company: Company,
    seed_role_admin: Role,
):
    """Проверка создания связи пользователя и компании"""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "user_id": str(seed_user.id),
        "company_id": str(seed_company.id),
        "role_id": str(seed_role_admin.id),
    }

    response = await test_app.post(
        "/api/user-company-relations/add", headers=headers, json=data
    )
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    assert "user_company_id" in response_data, "Не возвращается user_company_id!"

    relation = await UserCompanyRelation.filter(
        id=response_data["user_company_id"]
    ).first()
    assert relation is not None, "Связь не сохранена в БД!"


@pytest.mark.asyncio
async def test_get_user_company_relation(
    test_app: AsyncClient, jwt_token_admin: dict, seed_relation: UserCompanyRelation
):
    """Проверка просмотра одной связи"""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/user-company-relations/{seed_relation.id}",
        headers=headers,
    )
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )
    assert response.json()["user_company_id"] == str(seed_relation.id)


@pytest.mark.asyncio
async def test_update_user_company_relation(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_relation: UserCompanyRelation,
    seed_role_manager: Role,
):
    """Проверка изменения связи"""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    update_data = {"role_id": str(seed_role_manager.id)}
    response = await test_app.patch(
        f"/api/user-company-relations/{seed_relation.id}",
        headers=headers,
        json=update_data,
    )
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    # Проверяем, что только ID вернулся
    response_data = response.json()
    assert "user_company_id" in response_data, "В ответе нет user_company_id"
    assert response_data["user_company_id"] == str(seed_relation.id)

    # Проверяем в БД, загружая связанные данные
    relation = (
        await UserCompanyRelation.filter(id=seed_relation.id)
        .prefetch_related("role")
        .first()
    )
    assert relation is not None, "Связь не найдена в БД!"
    assert relation.role.name == "manager", (
        f"Роль не обновилась в БД! Ожидали 'manager', а получили '{relation.role.name}'"
    )


@pytest.mark.asyncio
async def test_delete_user_company_relation(
    test_app: AsyncClient, jwt_token_admin: dict, seed_relation: UserCompanyRelation
):
    """Проверка удаления связи"""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/user-company-relations/{seed_relation.id}",
        headers=headers,
    )
    assert response.status_code == 204, (
        f"Ошибка удаления: {response.status_code}, {response.text}"
    )

    # Проверяем, что связь действительно удалена
    relation = await UserCompanyRelation.filter(id=seed_relation.id).first()
    assert relation is None, "Связь не была удалена из БД!"


@pytest.mark.asyncio
async def test_get_all_user_company_relations(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_relation: UserCompanyRelation,  # noqa: F401
):
    """Проверка получения всех связей"""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/user-company-relations/all", headers=headers)
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    relations = response_data.get("relations")
    assert isinstance(relations, list), "Ответ должен быть списком!"
    assert response_data.get("total") >= 1
