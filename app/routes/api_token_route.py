# from fastapi import APIRouter, Depends, HTTPException, status

# from app.database.models import ApiToken, User, UserCompanyRelation
# from app.handlers.depends import require_permission_in_context
# from app.pydantic_models.api_tokens_models import *
# from app.utils.token_helpers import generate_token_hash  # функция хеширования
# from app.utils.validate_helpers import validate_exists

# token_router = APIRouter()


# @token_router.post(
#     "/add",
#     response_model=ApiTokenResponseSchema,
#     summary="Создать API токен",
#     status_code=status.HTTP_201_CREATED,
# )
# async def create_api_token(
#     data: ApiTokenCreateSchema,
#     context: dict = Depends(require_permission_in_context("add_api_token")),
# ):
#     await validate_exists(User, data.user_id, "Пользователь")

#     if not context.get("is_superadmin"):
#         related = await UserCompanyRelation.exists(
#             user_id=data.user_id, company_id=context["company"]
#         )
#         if not related:
#             raise HTTPException(
#                 status_code=403,
#                 detail="Пользователь не связан с вашей компанией",
#             )

#     raw_token = f"{data.user_id}-{data.application_id}-{datetime.utcnow().isoformat()}"
#     token_hash = generate_token_hash(raw_token)

#     token = await ApiToken.create(
#         user_id=data.user_id,
#         application_id=data.application_id,
#         token_hash=token_hash,
#         expires_at=data.expires_at,
#         comment=data.comment,
#     )

#     return {"api_token_id": token.id}
