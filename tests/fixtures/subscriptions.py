# conftest.py или отдельный файл fixtures/subscription.py

from datetime import date

import pytest

from app.database.models import (
    CompanySubscription,
    Subscription,
    SubscriptionDetails,
    SubscriptionPayments,
)


@pytest.fixture
async def seed_subscription(seed_application, seed_user):
    subscription = await Subscription.create(
        name="Тестовая подписка",
        price=199.0,
        application=seed_application,
        description="Описание",
        comment="Комментарий",
        created_by=seed_user.id,
        modified_by=seed_user.id,
    )
    return subscription


@pytest.fixture
async def seed_subscription_detail(seed_subscription, seed_user):
    detail = await SubscriptionDetails.create(
        subscription_id=seed_subscription.id,
        entity_name="TestEntity",
        bd_table="test_table",
        restriction=42,
        description="Test description",
        comment="Test comment",
        created_by=seed_user.id,
        modified_by=seed_user.id,
    )
    return detail


@pytest.fixture
async def seed_company_subscription(seed_user, seed_company, seed_subscription):
    subscription = await CompanySubscription.create(
        company=seed_company,
        subscription=seed_subscription,
        created_by=seed_user.id,
        modified_by=seed_user.id,
    )
    return subscription


@pytest.fixture
async def seed_subscription_payment(seed_company_subscription, seed_user):
    payment = await SubscriptionPayments.create(
        company_subscription_id=seed_company_subscription.id,
        payment_external_id="ext_123456",
        payment_date=date.today(),
        payment_amount=999.99,
        date_from=date(2025, 8, 1),
        date_to=date(2025, 9, 1),
        created_by=seed_user.id,
        modified_by=seed_user.id,
    )
    return payment
