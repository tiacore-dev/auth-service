from typing import Dict, List
from uuid import UUID

from fastapi import Depends, HTTPException, Path
from loguru import logger

from app.database.models import (
    EntityCompanyRelation,
    Permission,
    User,
    UserCompanyRelation,
)
from app.handlers.auth import get_current_user
from app.handlers.depends import require_permission_in_context


async def get_company_permissions_for_user(user: User) -> Dict[str, List[str]]:
    logger.debug(
        f"""🧩 user: {user} | type: {type(user)} |
          has is_superadmin: {hasattr(user, "is_superadmin")}"""
    )

    is_superadmin = getattr(user, "is_superadmin", False)
    if is_superadmin:
        logger.debug("👑 Пользователь супер админ — возвращаем универсальные права")
        return {"*": ["*"]}

    logger.debug("🔒 Пользователь не суперадмин — ищем права по компаниям")

    relations = await UserCompanyRelation.filter(user_id=user.id).select_related(
        "company", "role"
    )

    company_permissions = {}

    for rel in relations:
        perms = await Permission.filter(
            role_permission_relations__role=rel.role
        ).values_list("permission_id", flat=True)

        company_permissions[str(rel.company.id)] = list(perms)

    return company_permissions


def with_permission_and_company_check(permission: str):
    async def dependency(
        user_id: UUID = Path(..., description="ID пользователя"),
        context: dict = Depends(require_permission_in_context(permission)),
    ):
        if context.get("is_superadmin"):
            return context

        related_user_ids = await UserCompanyRelation.filter(
            company=context["company"]
        ).values_list("user_id", flat=True)

        if user_id not in related_user_ids:
            raise HTTPException(
                status_code=403,
                detail="""Вы не можете выполнять это действие
                  над пользователями других компаний""",
            )

        return context

    return Depends(dependency)


def with_exact_company_permission(permission: str):
    async def dependency(
        company_id: UUID = Path(..., description="ID компании"),
        user_data: dict = Depends(get_current_user),
    ):
        permissions = user_data.get("permissions")

        is_superadmin = user_data["is_superadmin"]

        if is_superadmin:
            return user_data
        if not isinstance(permissions, dict):
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        if (
            str(company_id) not in permissions
            or permission not in permissions[str(company_id)]
        ):
            raise HTTPException(status_code=403, detail="Недостаточно прав")

        email = user_data["email"]

        relation_exists = await UserCompanyRelation.filter(
            user__email=email, company__company_id=company_id
        ).exists()

        if not relation_exists:
            raise HTTPException(status_code=403, detail="Нет доступа к компании")

        return user_data

    return Depends(dependency)


def with_permission_and_user_company_check(permission: str):
    async def dependency(
        user_company_id: UUID = Path(
            ..., description="ID связи пользователя с компанией"
        ),
        context: dict = Depends(require_permission_in_context(permission)),
    ):
        if context.get("is_superadmin"):
            return context

        relation = await UserCompanyRelation.get_or_none(
            id=user_company_id
        ).prefetch_related("company")

        if not relation or str(relation.company.id) != str(context["company"]):
            raise HTTPException(
                status_code=403,
                detail="""Связь пользователя с компанией не найдена или не 
                принадлежит вашей компании""",
            )

        return context

    return Depends(dependency)


def with_permission_and_entity_company_check(permission: str):
    async def dependency(
        legal_entity_id: UUID = Path(..., description="ID юридического лица"),
        context: dict = Depends(require_permission_in_context(permission)),
    ):
        if context.get("is_superadmin"):
            return context

        # Проверка, связано ли это юр. лицо с компанией пользователя
        is_related = await EntityCompanyRelation.exists(
            legal_entity_id=legal_entity_id, company_id=context["company"]
        )

        if not is_related:
            raise HTTPException(
                status_code=403,
                detail="Вы не можете изменять юридические лица другой компании",
            )

        return context

    return Depends(dependency)


def with_permission_and_legal_entity_company_check(permission: str):
    async def dependency(
        relation_id: UUID = Path(..., description="ID связи компании и юрлица"),
        context: dict = Depends(require_permission_in_context(permission)),
    ):
        if context.get("is_superadmin"):
            return context

        relation = await EntityCompanyRelation.get_or_none(
            entity_company_relation_id=relation_id
        ).prefetch_related("company")

        if not relation or str(relation.company.company_id) != str(context["company"]):
            raise HTTPException(
                status_code=403,
                detail="Связь не принадлежит компании пользователя или не найдена",
            )

        return context

    return Depends(dependency)
