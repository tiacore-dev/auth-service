from collections import defaultdict
from typing import Dict, List
from uuid import UUID

from loguru import logger

from app.database.models import RoleIncludeRelation, RolePermissionRelation, User, UserCompanyRelation


async def get_company_permissions_for_user(
    user: User,
) -> Dict[str, Dict[str, List[dict]]] | None:
    if user.is_superadmin:
        return None

    relations = await UserCompanyRelation.filter(user=user).select_related("company", "role", "application")
    if not relations:
        return {}

    role_ids = {rel.role.id for rel in relations}
    role_id_to_name = {str(rel.role.id): rel.role.name for rel in relations}

    role_permissions = await RolePermissionRelation.filter(role_id__in=role_ids).select_related(
        "permission", "role", "restriction"
    )

    # role_id → List[permission.id]
    role_perm_map = defaultdict(list)
    for rp in role_permissions:
        role_perm_map[str(rp.role.id)].append(rp.permission.id)

    result: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for rel in relations:
        app_id = str(rel.application.id)
        company_id = str(rel.company.id)
        role_id = str(rel.role.id)
        role_name = role_id_to_name.get(role_id, "Неизвестная роль")
        perms = role_perm_map.get(role_id, [])

        result[app_id][company_id].append({"role": role_name, "permissions": perms})

    return result


async def get_company_permissions_by_application(
    user: User, application_id: str
) -> Dict[str, Dict[str, List[dict]]] | None:
    if user.is_superadmin:
        return None

    relations = await UserCompanyRelation.filter(user=user, application_id=application_id).select_related(
        "company", "role", "application"
    )

    if not relations:
        return {}

    role_ids = {rel.role.id for rel in relations}
    all_role_ids = await get_all_linked_role_ids(role_ids)
    # role_id_to_name = {str(rel.role.id): rel.role.name for rel in relations}

    role_permissions = await RolePermissionRelation.filter(role_id__in=all_role_ids).select_related(
        "permission", "role", "restriction"
    )

    role_perm_map = defaultdict(list)
    for rp in role_permissions:
        role_perm_map[str(rp.role.id)].append(rp.permission.id)

    result: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))

    for rel in relations:
        app_id = str(rel.application.id)
        company_id = str(rel.company.id)
        # Собираем union всех прав по all_role_ids
        all_perms = []
        for rid in all_role_ids:
            all_perms.extend(role_perm_map.get(str(rid), []))
        all_perms = list(set(all_perms))  # убираем дубли
        result[app_id][company_id].append({"role": rel.role.name, "permissions": all_perms})
    logger.debug(result)
    return result


async def get_all_linked_role_ids(role_ids: set[UUID]) -> set[UUID]:
    """
    Рекурсивно обходит граф включённых ролей и возвращает полный set id ролей (и начальные, и все вложенные).
    """
    visited = set(role_ids)
    queue = list(role_ids)
    while queue:
        role_id = queue.pop()
        children = await RoleIncludeRelation.filter(parent_role_id=role_id).values_list("child_role_id", flat=True)
        for child_id in children:
            if child_id not in visited:
                visited.add(child_id)  # type: ignore
                queue.append(child_id)  # type: ignore
    return visited
