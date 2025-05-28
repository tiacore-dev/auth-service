import pytest
from httpx import AsyncClient

from app.database.models import Company, User


@pytest.mark.asyncio
async def test_edit_user_no_permission(
    test_app: AsyncClient,
    get_token_for_user,
    user_no_permission: User,
    seed_other_user: User,
    seed_company_new: Company,
):
    token = await get_token_for_user(user_no_permission)
    response = await test_app.patch(
        f"/api/users/{seed_other_user.id}?company={seed_company_new.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Hacker"},
    )
    assert response.status_code == 403
    assert "Недостаточно прав" in response.text


@pytest.mark.asyncio
async def test_edit_user_wrong_company(
    test_app: AsyncClient,
    get_token_for_user,
    user_wrong_company: User,
    seed_other_user_wrong: User,
    seed_company_new: Company,
):
    token = await get_token_for_user(user_wrong_company)
    response = await test_app.patch(
        f"/api/users/{seed_other_user_wrong.id}?company={seed_company_new.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Wrong Place"},
    )
    assert response.status_code == 403
    assert "Вы не можете выполнять это действие" in response.text


@pytest.mark.asyncio
async def test_edit_user_with_access(
    test_app: AsyncClient,
    get_token_for_user,
    user_with_access: User,
    seed_other_user: User,
    seed_company_new: Company,
):
    token = await get_token_for_user(user_with_access)

    response = await test_app.patch(
        f"/api/users/{seed_other_user.id}?company={seed_company_new.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Correct User"},
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == str(seed_other_user.id)
