import pytest
from httpx import AsyncClient

from app.database.models import Application, Subscription


@pytest.mark.asyncio
async def test_add_subscription(test_app: AsyncClient, jwt_token_admin, seed_application: Application):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "subscription_name": "Подписка на аналитику",
        "price": 499.99,
        "application_id": str(seed_application.id),
        "description": "Полный доступ к модулю аналитики",
        "comment": "Для премиум-клиентов",
    }

    response = await test_app.post("/api/subscriptions/add", headers=headers, json=data)
    assert response.status_code == 201, response.text

    response_data = response.json()
    subscription = await Subscription.get_or_none(id=response_data["subscription_id"]).prefetch_related("application")
    assert subscription is not None
    assert subscription.name == "Подписка на аналитику"
    assert str(subscription.application.id) == str(seed_application.id)


@pytest.mark.asyncio
async def test_edit_subscription(test_app: AsyncClient, jwt_token_admin, seed_subscription: Subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"subscription_name": "Обновлённая подписка"}

    response = await test_app.patch(
        f"/api/subscriptions/{seed_subscription.id}",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200, response.text

    updated = await Subscription.get(id=seed_subscription.id)
    assert updated.name == "Обновлённая подписка"


@pytest.mark.asyncio
async def test_view_subscription(test_app: AsyncClient, jwt_token_admin, seed_subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(f"/api/subscriptions/{seed_subscription.id}", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["subscription_id"] == str(seed_subscription.id)
    assert data["subscription_name"] == seed_subscription.name


@pytest.mark.asyncio
async def test_delete_subscription(test_app: AsyncClient, jwt_token_admin, seed_subscription: Subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.delete(f"/api/subscriptions/{seed_subscription.id}", headers=headers)
    assert response.status_code == 204

    deleted = await Subscription.get_or_none(id=seed_subscription.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_subscription_list(test_app: AsyncClient, jwt_token_admin, seed_subscription: Subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/subscriptions/all", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] >= 1
    assert any(s["subscription_id"] == str(seed_subscription.id) for s in data["subscriptions"])
