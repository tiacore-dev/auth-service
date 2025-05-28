from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Path, Query
from loguru import logger

from app.database.models import UserCompanyRelation
from app.handlers.auth import get_current_user


async def get_current_context(
    token_data: dict = Depends(get_current_user),
    company: Optional[UUID] = Query(None, description="ID компании"),
):
    permissions_map = token_data.get("permissions", {})
    is_token_superadmin = token_data.get("is_superadmin")
    user_id = token_data["user_id"]
    logger.debug(f"[DEBUG TOKEN DATA] permissions={token_data['permissions']}")

    if is_token_superadmin:
        return {
            "user": user_id,
            "company": company,
            "role": "superadmin",
            "permissions": ["*"],
            "is_superadmin": True,
            "has_relations": True,
        }

    relations = await UserCompanyRelation.filter(user_id=user_id).all()
    has_relations = bool(relations)

    permissions = []
    if company:
        raw_entries = permissions_map.get(str(company), {})
        for entry in raw_entries:
            permissions.extend(entry.permissions)

        logger.debug(
            f"""[DEBUG CONTEXT] company={company}, raw={raw_entries}, 
            flat_permissions={permissions}"""
        )

    return {
        "user": user_id,
        "company": company,
        "role": None,
        "permissions": permissions,
        "is_superadmin": False,
        "has_relations": has_relations,
    }


def require_permission_in_context(permission: str):
    async def dependency(ctx=Depends(get_current_context)):
        if ctx["is_superadmin"]:
            return ctx
        if not ctx["has_relations"]:
            logger.info(
                f"""Пользователь {ctx["user"]} без связей — 
                доступ разрешён без проверки прав"""
            )
            return ctx
        if permission in ctx["permissions"]:
            return ctx
        logger.warning(
            f"Недостаточно прав для пользователя {ctx['user']}, требуется: {permission}"
        )
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return dependency


def require_permission_or_self_view(permission: str):
    async def dependency(
        ctx=Depends(get_current_context),
        user_id: UUID = Path(..., description="ID просматриваемого пользователя"),
    ):
        if ctx["is_superadmin"]:
            return ctx

        if not ctx["has_relations"]:
            logger.info(
                f"""Пользователь {ctx["user"]} без 
                связей — доступ разрешён без проверки прав"""
            )
            return ctx

        if str(ctx["user"]) == str(user_id):
            logger.info(
                f"Пользователь {ctx['user']} запрашивает сам себя — доступ разрешён"
            )
            return ctx

        if permission in ctx["permissions"]:
            return ctx

        logger.warning(
            f"Недостаточно прав для пользователя {ctx['user']}, требуется: {permission}"
        )
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return dependency
