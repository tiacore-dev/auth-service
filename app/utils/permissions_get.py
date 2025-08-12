from collections import defaultdict
from typing import Dict, List, Set, Tuple
from uuid import UUID

from app.database.models import (
    RoleIncludeRelation,
    RolePermissionRelation,
    User,
    UserCompanyRelation,
)

# --- helpers ---


async def _reachable_roles_and_adj(start_roles: Set[UUID]) -> Tuple[Set[UUID], dict[UUID, Set[UUID]]]:
    """
    BFS для всех стартовых ролей сразу.
    Возвращает:
      - visited: все достижимые роли (включая стартовые)
      - adj: adjacency list parent -> set(children)
    """
    visited: Set[UUID] = set(start_roles)
    frontier: Set[UUID] = set(start_roles)
    adj: dict[UUID, Set[UUID]] = defaultdict(set)

    while frontier:
        # за один проход тянем всех детей для текущего фронтира
        rows = await RoleIncludeRelation.filter(parent_role_id__in=frontier).values_list(
            "parent_role_id", "child_role_id"
        )
        frontier = set()
        for parent_id, child_id in rows:
            adj[parent_id].add(child_id)
            if child_id not in visited:
                visited.add(child_id)
                frontier.add(child_id)
    return visited, adj


def _closure_for_role(root: UUID, adj: dict[UUID, Set[UUID]]) -> Set[UUID]:
    """Строим замыкание роли по уже загруженному графу (в памяти)."""
    stack = [root]
    seen: Set[UUID] = {root}
    while stack:
        cur = stack.pop()
        for ch in adj.get(cur, ()):
            if ch not in seen:
                seen.add(ch)
                stack.append(ch)
    return seen


# --- основная функция ---


async def get_company_permissions_for_user(
    user: User,
) -> Dict[str, Dict[str, List[dict]]] | None:
    if user.is_superadmin:
        return None

    relations = await UserCompanyRelation.filter(user=user).select_related("company", "role", "application")
    if not relations:
        return {}

    # Уникальные базовые роли
    base_role_ids: Set[UUID] = {rel.role.id for rel in relations}
    role_id_to_name = {str(rel.role.id): rel.role.name for rel in relations}

    # 1) Один раз строим достижимые роли и граф включений
    all_roles_needed, adj = await _reachable_roles_and_adj(base_role_ids)

    # 2) Разворачиваем замыкание для каждой базовой роли в памяти
    closure_map: dict[str, Set[UUID]] = {}
    for rid in base_role_ids:
        closure_map[str(rid)] = _closure_for_role(rid, adj)

    # 3) Тянем права для всех ролей из объединённого множества одной выборкой
    #    Берём только нужные поля
    rp_rows = await RolePermissionRelation.filter(role_id__in=all_roles_needed).values_list("role_id", "permission_id")

    # role_id -> [permission_id(str)]
    role_perm_map: dict[str, List[str]] = defaultdict(list)
    for role_id, perm_id in rp_rows:
        role_perm_map[str(role_id)].append(str(perm_id))

    # 4) Собираем ответ: для каждой связи union прав по замыканию роли
    result: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for rel in relations:
        app_id = str(rel.application.id)
        company_id = str(rel.company.id)
        role_id_str = str(rel.role.id)

        perms_union: set[str] = set()
        for rid in closure_map[role_id_str]:
            perms_union.update(role_perm_map.get(str(rid), []))

        result[app_id][company_id].append(
            {
                "role": role_id_to_name.get(role_id_str, "Неизвестная роль"),
                "permissions": list(perms_union),  # <- строковые id, как тебе и нужно
            }
        )

    return result


# --- версия по одному приложению (без «перетеканий») ---


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

    base_role_ids: Set[UUID] = {rel.role.id for rel in relations}
    role_id_to_name = {str(rel.role.id): rel.role.name for rel in relations}

    # Один общий граф включений для всех ролей в этом приложении
    all_roles_needed, adj = await _reachable_roles_and_adj(base_role_ids)

    # Замыкание для каждой роли
    closure_map: dict[str, Set[UUID]] = {}
    for rid in base_role_ids:
        closure_map[str(rid)] = _closure_for_role(rid, adj)

    # Права для всех задействованных ролей
    rp_rows = await RolePermissionRelation.filter(role_id__in=all_roles_needed).values_list("role_id", "permission_id")
    role_perm_map: dict[str, List[str]] = defaultdict(list)
    for role_id, perm_id in rp_rows:
        role_perm_map[str(role_id)].append(str(perm_id))

    # Результат
    result: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for rel in relations:
        app_id = str(rel.application.id)  # = application_id
        company_id = str(rel.company.id)
        role_id_str = str(rel.role.id)

        perms_union: set[str] = set()
        for rid in closure_map[role_id_str]:
            perms_union.update(role_perm_map.get(str(rid), []))

        result[app_id][company_id].append(
            {
                "role": role_id_to_name.get(role_id_str, "Неизвестная роль"),
                "permissions": list(perms_union),
            }
        )

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
