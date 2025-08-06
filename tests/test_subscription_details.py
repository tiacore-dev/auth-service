import pytest
from httpx import AsyncClient

from app.database.models import Subscription, SubscriptionDetails


@pytest.mark.asyncio
async def test_add_subscription_detail(test_app: AsyncClient, jwt_token_admin, seed_subscription: Subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "subscription_id": str(seed_subscription.id),
        "entity_name": "Новое ограничение",
        "bd_table": "messages",
        "restriction": 100,
        "description": "Ограничение на количество сообщений",
        "comment": "Для теста",
    }

    response = await test_app.post("/api/subscription-details/add", headers=headers, json=data)
    assert response.status_code == 201, response.text

    response_data = response.json()
    detail = await SubscriptionDetails.get_or_none(id=response_data["subscription_details_id"])
    assert detail is not None
    assert detail.entity_name == "Новое ограничение"
    assert detail.bd_table == "messages"


@pytest.mark.asyncio
async def test_edit_subscription_detail(
    test_app: AsyncClient, jwt_token_admin, seed_subscription_detail: SubscriptionDetails
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"entity_name": "Обновлённое имя"}

    response = await test_app.patch(
        f"/api/subscription-details/{seed_subscription_detail.id}", headers=headers, json=data
    )
    assert response.status_code == 200, response.text

    updated = await SubscriptionDetails.get(id=seed_subscription_detail.id)
    assert updated.entity_name == "Обновлённое имя"


@pytest.mark.asyncio
async def test_get_subscription_detail(
    test_app: AsyncClient, jwt_token_admin, seed_subscription_detail: SubscriptionDetails
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(f"/api/subscription-details/{seed_subscription_detail.id}", headers=headers)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["subscription_detail_id"] == str(seed_subscription_detail.id)
    assert data["entity_name"] == seed_subscription_detail.entity_name


@pytest.mark.asyncio
async def test_delete_subscription_detail(
    test_app: AsyncClient, jwt_token_admin, seed_subscription_detail: SubscriptionDetails
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.delete(f"/api/subscription-details/{seed_subscription_detail.id}", headers=headers)
    assert response.status_code == 204

    deleted = await SubscriptionDetails.get_or_none(id=seed_subscription_detail.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_subscription_details_list(
    test_app: AsyncClient, jwt_token_admin, seed_subscription_detail: SubscriptionDetails
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/subscription-details/all", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] >= 1
    assert any(d["subscription_detail_id"] == str(seed_subscription_detail.id) for d in data["details"])
