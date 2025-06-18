from uuid import UUID

from fastapi import Depends, HTTPException, Path

from app.database.models import (
    UserCompanyRelation,
)
from app.handlers.auth import get_current_user
from app.handlers.depends import require_permission_in_context


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
