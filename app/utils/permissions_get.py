from collections import defaultdict
from typing import Dict, List

from app.database.models import RolePermissionRelation, User, UserCompanyRelation
from app.pydantic_models.auth_models import RolePermissionBlock


async def get_company_permissions_for_user(
    user: User, application_id: str
) -> Dict[str, List[RolePermissionBlock]] | None:
    if user.is_superadmin:
        return None

    relations = await UserCompanyRelation.filter(user=user).select_related(
        "company", "role"
    )

    filtered_relations = [
        rel for rel in relations if rel.role.application_id == application_id
    ]

    if not filtered_relations:
        return {}

    role_ids = {rel.role.id for rel in filtered_relations}
    role_id_to_name = {str(rel.role.id): rel.role.name for rel in filtered_relations}

    role_permissions = await RolePermissionRelation.filter(
        role_id__in=role_ids
    ).select_related("permission", "role")

    role_to_permissions = defaultdict(list)
    for rp in role_permissions:
        role_to_permissions[str(rp.role.id)].append(rp.permission.id)

    company_permissions: Dict[str, List[RolePermissionBlock]] = defaultdict(list)

    for rel in filtered_relations:
        company_id = str(rel.company.id)
        role_id = str(rel.role.id)
        role_name = role_id_to_name.get(role_id, "Неизвестная роль")
        permissions = role_to_permissions.get(role_id, [])

        company_permissions[company_id].append(
            RolePermissionBlock(role=role_name, permissions=permissions)
        )

    return dict(company_permissions)
