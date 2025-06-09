from collections import defaultdict
from typing import Dict, List

from app.database.models import RolePermissionRelation, User, UserCompanyRelation


async def get_company_permissions_for_user(
    user: User,
) -> Dict[str, Dict[str, List[dict]]] | None:
    if user.is_superadmin:
        return None

    relations = await UserCompanyRelation.filter(user=user).select_related(
        "company", "role"
    )
    if not relations:
        return {}

    role_ids = {rel.role.id for rel in relations}
    role_id_to_name = {str(rel.role.id): rel.role.name for rel in relations}

    role_permissions = await RolePermissionRelation.filter(
        role_id__in=role_ids
    ).select_related("permission", "role", "application")

    role_app_map = defaultdict(lambda: defaultdict(list))
    for rp in role_permissions:
        role_app_map[str(rp.role.id)][str(rp.application.id)].append(rp.permission.id)

    result: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for rel in relations:
        company_id = str(rel.company.id)
        role_id = str(rel.role.id)
        role_name = role_id_to_name.get(role_id, "Неизвестная роль")

        for app_id, perms in role_app_map[role_id].items():
            result[app_id][company_id].append({"role": role_name, "permissions": perms})

    return result


async def get_company_permissions_by_application(
    user: User, application_id: str
) -> Dict[str, Dict[str, List[dict]]] | None:
    if user.is_superadmin:
        return None

    relations = await UserCompanyRelation.filter(user=user).select_related(
        "company", "role"
    )
    if not relations:
        return {}

    role_ids = {rel.role.id for rel in relations}
    role_id_to_name = {str(rel.role.id): rel.role.name for rel in relations}

    role_permissions = await RolePermissionRelation.filter(
        role_id__in=role_ids, application_id=application_id
    ).select_related("permission", "role", "application")

    # (role_id, app_id) → List[permission_name]
    role_app_map = defaultdict(lambda: defaultdict(list))
    for rp in role_permissions:
        role_app_map[str(rp.role.id)][str(rp.application.id)].append(rp.permission.id)

    result: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for rel in relations:
        company_id = str(rel.company.id)
        role_id = str(rel.role.id)
        role_name = role_id_to_name.get(role_id, "Неизвестная роль")

        for app_id, perms in role_app_map[role_id].items():
            result[app_id][company_id].append({"role": role_name, "permissions": perms})

    return result
