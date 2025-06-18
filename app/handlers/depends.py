from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Path, Query
from loguru import logger
from tiacore_lib.config import get_settings
from tiacore_lib.pydantic_models.auth_models import RolePermissionBlock

from app.database.models import UserCompanyRelation
from app.handlers.auth import get_current_user


async def get_current_context(
    token_data: dict = Depends(get_current_user),
    company: Optional[UUID] = Query(None, description="ID компании"),
    settings=Depends(get_settings),
):
    permissions_map = token_data.get("permissions", {})
    is_token_superadmin = token_data.get("is_superadmin")
    user_id = token_data["user_id"]
    logger.debug(f"[DEBUG TOKEN DATA] permissions={token_data['permissions']}")
    application = settings.APP
    if is_token_superadmin:
        return {
            "user": user_id,
            "company": company,
            "application": application,
            "role": "superadmin",
            "permissions": ["*"],
            "is_superadmin": True,
            "has_relations": True,
        }

    relations = await UserCompanyRelation.filter(user_id=user_id).all()
    has_relations = bool(relations)

    permissions = []
    raw_blocks = []

    if company and application:
        raw_entries = permissions_map.get(application, {}).get(str(company), [])
        for entry in raw_entries:
            if isinstance(entry, dict):
                entry = RolePermissionBlock(**entry)
            permissions.extend(entry.permissions)
            raw_blocks.append(entry)

        logger.debug(
            f"[DEBUG CONTEXT] application={application}, company={company}, "
            f"raw={raw_entries}, flat_permissions={permissions}"
        )

    return {
        "user": user_id,
        "company": company,
        "application": application,
        "permissions": permissions,
        "raw_permission_blocks": raw_blocks,
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

        if str(ctx["user_id"]) == str(user_id):
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
