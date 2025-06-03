import pytest
from httpx import AsyncClient

from app.database.models import Application


@pytest.mark.asyncio
async def test_get_applications(
    test_app: AsyncClient, jwt_token_admin: dict, seed_application: Application
):
    """Тест получения списка разрешений с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/applications/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    applications = response_data.get("applications")
    assert isinstance(applications, list), "Ответ должен быть списком"
    assert response_data.get("total") > 0

    application_ids = [perm["application_id"] for perm in applications]
    assert str(seed_application.id) in application_ids, (
        "Приложение отсутствует в списке"
    )
