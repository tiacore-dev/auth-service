# tests/test_role_includes.py

import pytest
from httpx import AsyncClient

from app.database.models import (
    Application,
    Company,
    Permission,
    Role,
    RoleIncludeRelation,
    RolePermissionRelation,
    User,
    UserCompanyRelation,
)
from app.utils.permissions_get import (
    get_company_permissions_by_application,
    get_company_permissions_for_user,
)

API_PREFIX = "/api/include-roles"


# =========================
# Фикстуры
# =========================


@pytest.fixture
async def apps():
    # pk — строковые id (например: "auth_app")
    auth, _ = await Application.get_or_create(id="auth_app", defaults={"name": "Auth"})
    price, _ = await Application.get_or_create(id="price_app", defaults={"name": "Price"})
    parcel, _ = await Application.get_or_create(id="parcel_app", defaults={"name": "Parcel"})
    return {"auth": auth, "price": price, "parcel": parcel}


@pytest.fixture
async def seed_company_new():
    return await Company.create(name="ACME, Inc.")


@pytest.fixture
async def user_with_access():
    # не супер-админ, чтобы включилась бизнес-логика прав
    return await User.create_user(
        email="u@test.local",
        password="pass",
        full_name="User Test",
        is_superadmin=False,
        is_verified=True,
    )


@pytest.fixture
async def permissions_basic():
    """
    Пермишены со строковыми id (pk) и обязательным полем name.
    """

    async def mk(pid: str):
        obj, _ = await Permission.get_or_create(id=pid, defaults={"name": pid})
        return obj

    return {
        "view_user": await mk("view_user"),
        "edit_user": await mk("edit_user"),
        "add_price": await mk("add_price"),
    }


@pytest.fixture
async def roles_basic(apps):
    """
    Две роли в разных приложениях:
      - role_auth с application_id="auth_app"
      - role_price с application_id="price_app"
    """
    role_auth = await Role.create(name="Админ Аутентификации", application_id="auth_app")
    role_price = await Role.create(name="Админ Тарифов", application_id="price_app")
    return {"role_auth": role_auth, "role_price": role_price}


@pytest.fixture
async def role_with_edit_user(roles_basic, permissions_basic):
    # auth-роль с базовыми правами
    role = roles_basic["role_auth"]
    await RolePermissionRelation.get_or_create(role=role, permission=permissions_basic["view_user"])
    await RolePermissionRelation.get_or_create(role=role, permission=permissions_basic["edit_user"])
    return role


@pytest.fixture
async def other_role(roles_basic, permissions_basic):
    # price-роль с правом add_price
    role = roles_basic["role_price"]
    await RolePermissionRelation.get_or_create(role=role, permission=permissions_basic["add_price"])
    return role


@pytest.fixture
async def user_role(roles_basic):
    # ещё одна ссылка на auth-роль (для проверки цикла)
    return roles_basic["role_auth"]


@pytest.fixture
async def role_graph(role_with_edit_user, other_role, user_with_access):
    """
    include: AUTH-роль включает PRICE-роль (cross-app).
    RoleIncludeRelation требует created_by/modified_by.
    """
    rel, _ = await RoleIncludeRelation.get_or_create(
        parent_role=role_with_edit_user,
        child_role=other_role,
        defaults={
            "created_by": user_with_access.id,
            "modified_by": user_with_access.id,
        },
    )
    return rel


@pytest.fixture
async def bind_user_company_in_auth(user_with_access, seed_company_new, role_with_edit_user, apps):
    """
    Привязка пользователя к компании в контексте auth_app.
    Важно: application — FK, поэтому передаём объект Application.
    """
    await UserCompanyRelation.get_or_create(
        user=user_with_access,
        company=seed_company_new,
        role=role_with_edit_user,
        application=apps["auth"],
    )
    return True


# =========================
# API-тесты include-ролей
# =========================


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
async def test_cycle_protection(test_app: AsyncClient, jwt_token_admin, role_with_edit_user, other_role, role_graph):
    # role_graph уже создал связь: role_with_edit_user -> other_role
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    # Пытаемся замкнуть граф: other_role -> role_with_edit_user
    resp = await test_app.post(
        f"{API_PREFIX}/add",
        headers=headers,
        json={
            "parent_role_id": str(other_role.id),
            "child_role_id": str(role_with_edit_user.id),
        },
    )
    assert resp.status_code == 400, resp.text
    detail = resp.json().get("detail", "").lower()
    assert ("цикл" in detail) or ("cycle" in detail)


@pytest.mark.asyncio
async def test_self_include_forbidden(test_app: AsyncClient, jwt_token_admin, role_with_edit_user):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    resp = await test_app.post(
        f"{API_PREFIX}/add",
        headers=headers,
        json={
            "parent_role_id": str(role_with_edit_user.id),
            "child_role_id": str(role_with_edit_user.id),
        },
    )
    assert resp.status_code == 400, resp.text
    assert "саму себя" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_delete_role_include_relation(
    test_app: AsyncClient, jwt_token_admin, role_with_edit_user, other_role, role_graph
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    rel = await RoleIncludeRelation.filter(parent_role=role_with_edit_user, child_role=other_role).first()
    resp = await test_app.delete(f"{API_PREFIX}/{rel.id}", headers=headers)  # type: ignore
    assert resp.status_code == 204, resp.text
    assert not await RoleIncludeRelation.filter(id=rel.id).exists()  # type: ignore


# =========================
# Бизнес-логика прав
# =========================


@pytest.mark.asyncio
async def test_permission_union_via_graph_by_app(
    user_with_access, role_graph, seed_company_new, bind_user_company_in_auth
):
    """
    Проверяем get_company_permissions_by_application:
    — у пользователя базовая связь в auth_app,
    — базовые права (edit_user, view_user) должны присутствовать в ветке auth_app.
    """
    permissions = await get_company_permissions_by_application(user=user_with_access, application_id="auth_app")
    result_perms = set()
    for app_data in permissions.values():  # type: ignore
        for company_data in app_data.values():
            for rel in company_data:
                result_perms.update(rel["permissions"])
    assert "edit_user" in result_perms
    assert "view_user" in result_perms


@pytest.mark.asyncio
async def test_cross_app_distribution_to_price(
    user_with_access, apps, seed_company_new, role_graph, bind_user_company_in_auth
):
    """
    Кросс-app распределение:
    — базовая связь в auth_app,
    — через include подтягиваются роли из price_app,
    — права price-ролей должны появиться в ветке price_app той же компании.
    """
    dist = await get_company_permissions_for_user(user_with_access)
    assert dist is not None
    price_tree = dist.get("price_app", {})
    company_id = str(seed_company_new.id)
    assert company_id in price_tree, f"В price_app отсутствует company {company_id}"
    perms_union = set()
    for rel in price_tree[company_id]:
        perms_union.update(rel["permissions"])
    assert "add_price" in perms_union, "Ожидали право из роли price_app, полученной через include"


@pytest.mark.asyncio
async def test_company_isolation(user_with_access, apps, role_with_edit_user):
    """
    Изоляция по компаниям:
    — юзер привязан к company A,
    — у company B не должно быть прав.
    """
    company_a = await Company.create(name="A")
    company_b = await Company.create(name="B")

    await UserCompanyRelation.create(
        user=user_with_access,
        company=company_a,
        role=role_with_edit_user,
        application=apps["auth"],
    )

    dist = await get_company_permissions_for_user(user_with_access)
    assert dist is not None

    auth_tree = dist.get("auth_app", {})
    assert str(company_a.id) in auth_tree
    assert str(company_b.id) not in auth_tree
