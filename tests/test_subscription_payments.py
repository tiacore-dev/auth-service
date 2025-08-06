from datetime import date

import pytest
from httpx import AsyncClient

from app.database.models import SubscriptionPayments


@pytest.mark.asyncio
async def test_add_subscription_payment(test_app: AsyncClient, jwt_token_admin, seed_company_subscription):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "company_subscription_id": str(seed_company_subscription.id),
        "payment_external_id": "ext_9999",
        "payment_date": str(date.today()),
        "payment_amount": 500.0,
        "date_from": "2025-08-01",
        "date_to": "2025-09-01",
    }

    response = await test_app.post("/api/subscription-payments/add", headers=headers, json=data)
    assert response.status_code == 201, response.text

    response_data = response.json()
    payment = await SubscriptionPayments.get_or_none(id=response_data["subscription_payment_id"])
    assert payment is not None
    assert payment.payment_amount == 500.0


@pytest.mark.asyncio
async def test_edit_subscription_payment(test_app: AsyncClient, jwt_token_admin, seed_subscription_payment):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"payment_amount": 777.0}

    response = await test_app.patch(
        f"/api/subscription-payments/{seed_subscription_payment.id}",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200, response.text

    updated = await SubscriptionPayments.get(id=seed_subscription_payment.id)
    assert updated.payment_amount == 777.0


@pytest.mark.asyncio
async def test_get_subscription_payment(test_app: AsyncClient, jwt_token_admin, seed_subscription_payment):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(f"/api/subscription-payments/{seed_subscription_payment.id}", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["subscription_payment_id"] == str(seed_subscription_payment.id)
    assert data["payment_amount"] == seed_subscription_payment.payment_amount


@pytest.mark.asyncio
async def test_delete_subscription_payment(test_app: AsyncClient, jwt_token_admin, seed_subscription_payment):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.delete(f"/api/subscription-payments/{seed_subscription_payment.id}", headers=headers)
    assert response.status_code == 204

    deleted = await SubscriptionPayments.get_or_none(id=seed_subscription_payment.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_subscription_payments_list(test_app: AsyncClient, jwt_token_admin, seed_subscription_payment):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/subscription-payments/all", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] >= 1
    assert any(p["subscription_payment_id"] == str(seed_subscription_payment.id) for p in data["payments"])
