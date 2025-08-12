from collections import defaultdict
from typing import Dict, List, Set, Tuple
from uuid import UUID

from app.database.models import (
    Role,
    RoleIncludeRelation,
    RolePermissionRelation,
    User,
    UserCompanyRelation,
)

# --- helpers ---


async def _reachable_roles_and_adj(start_roles: Set[UUID]) -> Tuple[Set[UUID], dict[UUID, Set[UUID]]]:
    """BFS по графу включений для всех стартовых ролей сразу."""
    visited: Set[UUID] = set(start_roles)
    frontier: Set[UUID] = set(start_roles)
    adj: dict[UUID, Set[UUID]] = defaultdict(set)
    while frontier:
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
    """Все роли, достижимые из root (включая root)."""
    stack = [root]
    seen: Set[UUID] = {root}
    while stack:
        cur = stack.pop()
        for ch in adj.get(cur, ()):
            if ch not in seen:
                seen.add(ch)
                stack.append(ch)
    return seen


# --- основное распределение ---


async def get_company_permissions_for_user(
    user: User,
) -> Dict[str, Dict[str, List[dict]]] | None:
    """
    Результат: app_id -> company_id -> [ { role: <role_name>, permissions: [perm_id, ...] }, ... ]

    КАЖДАЯ роль из closure распределяется в СВОЙ app (cross-app).
    """
    if user.is_superadmin:
        return None

    relations = await UserCompanyRelation.filter(user=user).select_related("company", "role", "application")
    if not relations:
        return {}

    # 1) Базовые роли и сопутствующие мапы
    base_role_ids: Set[UUID] = {rel.role.id for rel in relations}

    # 2) Closure по всем базовым ролям сразу (один раз строим граф)
    all_roles_needed, adj = await _reachable_roles_and_adj(base_role_ids)

    # Замыкание для каждой базовой роли
    closure_map: dict[UUID, Set[UUID]] = {rid: _closure_for_role(rid, adj) for rid in base_role_ids}

    # 3) Метаданные ролей: app и имя
    role_meta_rows = await Role.filter(id__in=all_roles_needed).values_list("id", "application_id", "name")
    role_app_map: dict[UUID, str] = {}
    role_name_map: dict[UUID, str] = {}
    for rid, app_id, name in role_meta_rows:
        role_app_map[rid] = str(app_id)
        role_name_map[rid] = name

    # 4) Права ролей (только нужные поля)
    rp_rows = await RolePermissionRelation.filter(role_id__in=all_roles_needed).values_list("role_id", "permission_id")
    role_perm_map: dict[UUID, List[str]] = defaultdict(list)
    for role_id, perm_id in rp_rows:
        role_perm_map[role_id].append(str(perm_id))  # строковые id, как нужно

    # 5) Копим union по ключу (target_app_id, company_id, target_role_id)
    bucket: dict[tuple[str, str, UUID], set[str]] = defaultdict(set)

    for rel in relations:
        company_id = str(rel.company.id)
        base_rid: UUID = rel.role.id

        # Каждую роль из closure раскидываем в ЕЁ app
        for rid in closure_map[base_rid]:
            target_app_id = role_app_map.get(rid)
            if not target_app_id:
                continue
            perms = role_perm_map.get(rid, [])
            if not perms:
                continue
            bucket[(target_app_id, company_id, rid)].update(perms)

    # 6) Формируем требуемую структуру
    result: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for (app_id, company_id, rid), perms in bucket.items():
        result[app_id][company_id].append(
            {
                "role": role_name_map.get(rid, "Неизвестная роль"),
                "permissions": sorted(perms),
            }
        )

    return result


# --- версия по одному приложению: фильтруем готовое распределение ---


async def get_company_permissions_by_application(
    user: User, application_id: str
) -> Dict[str, Dict[str, List[dict]]] | None:
    """
    Возвращает распределение ТОЛЬКО для указанного app_id,
    но учитывает cross-app включения (если в closure есть роли целевого app — они попадут сюда).
    """
    dist = await get_company_permissions_for_user(user)
    if dist is None:
        return None
    # Оставляем только нужный app
    return {application_id: dist.get(application_id, {})}
