import pytest
from httpx import AsyncClient

from app.database.models import Company


@pytest.mark.asyncio
async def test_add_company(test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "company_name": "Test Company Added",
        "description": "Описание тестовой компании",
    }

    response = await test_app.post("/api/companies/add", headers=headers, json=data)
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    company = await Company.get_or_none(id=response_data["company_id"])
    assert company is not None
    assert company.name == "Test Company Added"


@pytest.mark.asyncio
async def test_edit_company(
    test_app: AsyncClient, jwt_token_admin, seed_company: Company
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "company_name": "Updated Company Name",
        "description": "Обновленное описание",
    }

    response = await test_app.patch(
        f"/api/companies/{seed_company.id}", headers=headers, json=data
    )
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    updated_company = await Company.get_or_none(id=seed_company.id)
    assert updated_company is not None
    assert updated_company.name == "Updated Company Name"
    assert updated_company.description == "Обновленное описание"


@pytest.mark.asyncio
async def test_view_company(
    test_app: AsyncClient, jwt_token_admin, seed_company: Company
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/companies/{seed_company.id}", headers=headers)
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    assert data["company_id"] == str(seed_company.id)
    assert data["company_name"] == seed_company.name
    assert data["description"] == seed_company.description


@pytest.mark.asyncio
async def test_delete_company(
    test_app: AsyncClient, jwt_token_admin, seed_company: Company
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/companies/{seed_company.id}", headers=headers
    )
    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    deleted = await Company.get_or_none(id=seed_company.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_companies(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_company: Company,
    seed_relation,  # noqa
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/companies/all", headers=headers)
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    companies = data["companies"]

    assert data["total"] >= 1
    assert isinstance(companies, list)
    assert any(company["company_id"] == str(seed_company.id) for company in companies)
