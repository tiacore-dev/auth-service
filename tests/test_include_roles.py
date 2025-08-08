import pytest
from httpx import AsyncClient

from app.database.models import RoleIncludeRelation
from app.utils.permissions_get import get_company_permissions_by_application

API_PREFIX = "/api/include-roles"


@pytest.mark.asyncio
async def test_create_role_include_relation(test_app: AsyncClient, jwt_token_admin, role_with_edit_user, other_role):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    resp = await test_app.post(
        f"{API_PREFIX}/add",
        headers=headers,
        json={
            "parent_role_id": str(role_with_edit_user.id),
            "child_role_id": str(other_role.id),
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "role_include_relation_id" in data


@pytest.mark.asyncio
async def test_cycle_protection(
    test_app: AsyncClient, jwt_token_admin, role_with_edit_user, other_role, user_role, role_graph
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    # Пытаемся создать обратную связь — цикл!
    resp = await test_app.post(
        f"{API_PREFIX}/add",
        headers=headers,
        json={
            "parent_role_id": str(user_role.id),
            "child_role_id": str(role_with_edit_user.id),
        },
    )
    assert resp.status_code == 400, resp.text
    assert "цикл" in resp.text.lower()


@pytest.mark.asyncio
async def test_delete_role_include_relation(
    test_app: AsyncClient, jwt_token_admin, role_with_edit_user, other_role, role_graph
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    rel = await RoleIncludeRelation.filter(parent_role=role_with_edit_user, child_role=other_role).first()
    resp = await test_app.delete(f"{API_PREFIX}/{rel.id}", headers=headers)  # type:ignore
    assert resp.status_code == 204, resp.text
    assert not await RoleIncludeRelation.filter(id=rel.id).exists()  # type:ignore


@pytest.mark.asyncio
async def test_permission_union_via_graph(user_with_access, role_graph, seed_company_new):
    # Тут авторизация не нужна — тестируем чистую бизнес-логику
    permissions = await get_company_permissions_by_application(user=user_with_access, application_id="auth_app")
    # Сравниваем формат и наличие нужных пермишенов
    result_perms = set()
    for app_data in permissions.values():  # type:ignore
        for company_data in app_data.values():
            for rel in company_data:
                result_perms.update(rel["permissions"])
    assert "edit_user" in result_perms
    assert "view_user" in result_perms
