import pytest
from httpx import AsyncClient

from app.database.models import CompanySubscription


@pytest.mark.asyncio
async def test_add_company_subscription(test_app: AsyncClient, jwt_token_admin, seed_company, seed_subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "company_id": str(seed_company.id),
        "subscription_id": str(seed_subscription.id),
    }

    response = await test_app.post("/api/company-subscriptions/add", headers=headers, json=data)
    assert response.status_code == 201, response.text

    response_data = response.json()
    obj = await CompanySubscription.get_or_none(id=response_data["company_subscription_id"]).prefetch_related(
        "subscription", "company"
    )
    assert obj is not None
    assert obj.subscription.id == seed_subscription.id
    assert obj.company.id == seed_company.id


@pytest.mark.asyncio
async def test_edit_company_subscription(
    test_app: AsyncClient, jwt_token_admin, seed_company_subscription, seed_company_new
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "company_id": str(seed_company_new.id),
    }

    response = await test_app.patch(
        f"/api/company-subscriptions/{seed_company_subscription.id}", headers=headers, json=data
    )
    assert response.status_code == 200, response.text

    updated = await CompanySubscription.get(id=seed_company_subscription.id).prefetch_related("company")
    assert str(updated.company.id) == str(seed_company_new.id)


@pytest.mark.asyncio
async def test_get_company_subscription(test_app: AsyncClient, jwt_token_admin, seed_company_subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(f"/api/company-subscriptions/{seed_company_subscription.id}", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["company_subscription_id"] == str(seed_company_subscription.id)
    assert data["subscription_id"] == str(seed_company_subscription.subscription_id)


@pytest.mark.asyncio
async def test_delete_company_subscription(test_app: AsyncClient, jwt_token_admin, seed_company_subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.delete(f"/api/company-subscriptions/{seed_company_subscription.id}", headers=headers)
    assert response.status_code == 204

    deleted = await CompanySubscription.get_or_none(id=seed_company_subscription.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_company_subscription_list(test_app: AsyncClient, jwt_token_admin, seed_company_subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/company-subscriptions/all", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] >= 1
    assert any(sub["company_subscription_id"] == str(seed_company_subscription.id) for sub in data["subscriptions"])
