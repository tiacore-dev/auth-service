from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from loguru import logger
from tiacore_lib.pydantic_models.api_tokens_models import (
    ApiTokenCreateSchema,
    ApiTokenResponseSchema,
)
from tiacore_lib.utils.validate_helpers import validate_exists

from app.database.models import ApiToken, User, UserCompanyRelation
from app.handlers.depends import require_permission_in_context
from app.handlers.token import generate_token_pair  # функция хеширования

token_router = APIRouter()


@token_router.post(
    "/add",
    response_model=ApiTokenResponseSchema,
    summary="Создать API токен",
    status_code=status.HTTP_201_CREATED,
)
async def create_api_token(
    data: ApiTokenCreateSchema,
    context: dict = Depends(require_permission_in_context("add_api_token")),
):
    await validate_exists(User, data.user_id, "Пользователь")

    if not context.get("is_superadmin"):
        related = await UserCompanyRelation.exists(
            user_id=data.user_id, api_token_id=context["api_token"]
        )
        if not related:
            raise HTTPException(
                status_code=403,
                detail="Пользователь не связан с вашей компанией",
            )

    raw_token, token_hash = generate_token_pair()

    token = await ApiToken.create(
        user_id=data.user_id,
        application_id=data.application_id,
        token_hash=token_hash,
        expires_at=data.expires_at,
        comment=data.comment,
    )

    return {"api_token_id": token.id, "api_token": raw_token}


@token_router.delete(
    "/{api_token_id}",
    summary="Удаление компании",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_api_token(
    api_token_id: UUID = Path(
        ..., title="ID компании", description="ID удаляемой компании"
    ),
    _=Depends(require_permission_in_context("delete_api_token")),
):
    logger.info(f"Удаление компании: {api_token_id}")

    api_token = await ApiToken.filter(id=api_token_id).first()
    if not api_token:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    await api_token.delete()
    logger.success(f"Компания {api_token_id} успешно удалена")
