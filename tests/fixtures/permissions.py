import pytest

from app.database.models import (
    Application,
    Company,
    Permission,
    Role,
    RolePermissionRelation,
    UserCompanyRelation,
    create_user,
)


@pytest.fixture
async def permission_edit_user():
    return await Permission.create(id="edit_user", name="User Editor")


@pytest.fixture
async def permission_view_user():
    return await Permission.create(id="view_user", name="Просмотр пользователя")


@pytest.fixture
async def seed_application():
    return await Application.create(
        id="test_app", name="Test App", system_name="test_app"
    )


@pytest.fixture
async def role_with_edit_user(permission_edit_user, seed_application):
    role = await Role.create(
        name="editor", system_name="admin", application=seed_application
    )
    await RolePermissionRelation.create(role=role, permission=permission_edit_user)
    return role


@pytest.fixture
async def other_role(permission_view_user, seed_application):
    role = await Role.create(name="no_permission", application=seed_application)
    await RolePermissionRelation.create(role=role, permission=permission_view_user)
    return role


@pytest.fixture
async def user_role(seed_application):
    role = await Role.create(
        name="Пользователь", system_name="user", application=seed_application
    )
    return role


@pytest.fixture
async def seed_company_new():
    return await Company.create(name="TestCompany", description="...")


@pytest.fixture
async def other_company():
    return await Company.create(name="OtherCompany", description="...")


@pytest.fixture
async def seed_other_user(seed_company_new, other_role):
    user = await create_user(
        email="Test User", password="123", full_name="User", position="user"
    )
    user.is_verified = True
    await user.save()
    await UserCompanyRelation.create(
        user=user, company=seed_company_new, role=other_role
    )
    return user


@pytest.fixture
async def seed_other_user_wrong(other_company, other_role):
    user = await create_user(
        email="Test User", password="123", full_name="User", position="user"
    )
    user.is_verified = True
    await user.save()
    await UserCompanyRelation.create(user=user, company=other_company, role=other_role)
    return user


# 1. Без прав


@pytest.fixture
async def user_no_permission(seed_company_new, other_role):
    user = await create_user(
        email="noperm", full_name="No Perm", position="Dev", password="123"
    )
    user.is_verified = True
    await user.save()
    await UserCompanyRelation.create(
        user=user, company=seed_company_new, role=other_role
    )
    return user


# 2. С правами, но в другой компании


@pytest.fixture
async def user_wrong_company(role_with_edit_user, seed_company_new):
    user = await create_user(
        email="wrongco", full_name="Wrong Co", position="Dev", password="123"
    )
    user.is_verified = True
    await user.save()
    await UserCompanyRelation.create(
        user=user, company=seed_company_new, role=role_with_edit_user
    )
    return user


# 3. С правами и в нужной компании


@pytest.fixture
async def user_with_access(role_with_edit_user, seed_company_new):
    user = await create_user(
        email="withaccess", full_name="With Access", position="Dev", password="123"
    )
    user.is_verified = True
    await user.save()
    await UserCompanyRelation.create(
        user=user, company=seed_company_new, role=role_with_edit_user
    )
    return user
