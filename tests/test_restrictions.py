import pytest
from httpx import AsyncClient

from app.database.models import Restriction


@pytest.mark.asyncio
async def test_get_restrictions(
    test_app: AsyncClient, jwt_token_admin: dict, seed_restriction: Restriction
):
    """Тест получения списка разрешений с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/restrictions/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    restrictions = response_data.get("restrictions")
    assert isinstance(restrictions, list), "Ответ должен быть списком"
    assert response_data.get("total") > 0

    restriction_ids = [perm["restriction_id"] for perm in restrictions]
    assert str(seed_restriction.id) in restriction_ids, (
        "Разрешение отсутствует в списке"
    )
