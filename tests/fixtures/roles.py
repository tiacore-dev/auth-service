import pytest

from app.database.models import RoleIncludeRelation


@pytest.fixture
async def role_graph(role_with_edit_user, other_role, user_role, seed_user):
    """
    Граф:
    - role_with_edit_user (editor) включает other_role (no_permission)
    - other_role (no_permission) включает user_role (Пользователь)
    """
    await RoleIncludeRelation.create(
        parent_role=role_with_edit_user,
        child_role=other_role,
        created_by=seed_user.id,
        modified_by=seed_user.id,
    )
    await RoleIncludeRelation.create(
        parent_role=other_role,
        child_role=user_role,
        created_by=seed_user.id,
        modified_by=seed_user.id,
    )
