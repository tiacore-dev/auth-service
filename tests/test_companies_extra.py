import pytest


@pytest.mark.asyncio
async def test_get_companies_search(
    test_app, jwt_token_admin, seed_company, seed_relation
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/companies/all?search=Test", headers=headers)

    assert response.status_code == 200
    companies = response.json()["companies"]
    assert any("Test" in c["company_name"] for c in companies)


@pytest.mark.asyncio
async def test_add_company_short_name(test_app, jwt_token_admin, seed_application):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "company_name": "ab",
        "description": "fail",
        "application_id": str(seed_application.id),
    }

    response = await test_app.post("/api/companies/add", headers=headers, json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_nonexistent_company(test_app, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    non_existent_id = "11111111-1111-1111-1111-111111111111"

    response = await test_app.delete(
        f"/api/companies/{non_existent_id}", headers=headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_superadmin_can_view_all(test_app, jwt_token_admin, seed_company):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/companies/all", headers=headers)

    assert response.status_code == 200
    companies = response.json()["companies"]
    assert any(c["company_id"] == str(seed_company.id) for c in companies)
