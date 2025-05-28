import pytest
from httpx import AsyncClient

from app.database.models import RolePermissionRelation


@pytest.mark.asyncio
async def test_add_role_permission_relation(
    test_app: AsyncClient, jwt_token_admin, seed_role_admin, seed_permission
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"role_id": str(seed_role_admin.id), "permission_id": seed_permission.id}

    response = await test_app.post(
        "/api/role-permission-relations/add", headers=headers, json=data
    )
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    assert "role_permission_id" in response_data
    relation = await RolePermissionRelation.get_or_none(
        id=response_data["role_permission_id"]
    )
    assert relation is not None


@pytest.mark.asyncio
async def test_update_role_permission_relation(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_role_permission_relation,
    seed_role_manager,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    update_data = {"role_id": str(seed_role_manager.id)}

    response = await test_app.patch(
        f"/api/role-permission-relations/{seed_role_permission_relation.id}",
        headers=headers,
        json=update_data,
    )
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )
    response_data = response.json()
    assert response_data["role_permission_id"] == str(seed_role_permission_relation.id)

    updated = await RolePermissionRelation.get(
        id=seed_role_permission_relation.id
    ).prefetch_related("role")
    assert str(updated.role.id) == str(seed_role_manager.id)


@pytest.mark.asyncio
async def test_delete_role_permission_relation(
    test_app: AsyncClient, jwt_token_admin, seed_role_permission_relation
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.delete(
        f"/api/role-permission-relations/{seed_role_permission_relation.id}",
        headers=headers,
    )

    assert response.status_code == 204
    relation = await RolePermissionRelation.get_or_none(
        id=seed_role_permission_relation.id
    )
    assert relation is None


@pytest.mark.asyncio
async def test_get_role_permission_relation(
    test_app: AsyncClient, jwt_token_admin, seed_role_permission_relation
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(
        f"/api/role-permission-relations/{seed_role_permission_relation.id}",
        headers=headers,
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )
    assert response.json()["role_permission_id"] == str(
        seed_role_permission_relation.id
    )


@pytest.mark.asyncio
async def test_get_all_role_permission_relations(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_role_permission_relation,  # noqa: F401
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/role-permission-relations/all", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("relations"), list)
    assert data.get("total", 0) >= 1
