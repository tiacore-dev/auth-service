# from datetime import datetime
# from uuid import UUID

# from pydantic import BaseModel, Field


# class ApiTokenCreateSchema(BaseModel):
#     user_id: UUID
#     application_id: str
#     expires_at: datetime | None = None
#     comment: str | None = None


# class ApiTokenResponseSchema(BaseModel):
#     id: UUID = Field(..., alias="api_token_id")


# class ApiTokenSchema(BaseModel):
#     id: UUID
#     user_id: UUID
#     application_id: str
#     token_hash: str
#     created_at: datetime
#     expires_at: datetime | None
#     comment: str | None


# class ApiTokenListResponseSchema(BaseModel):
#     total: int
#     tokens: list[ApiTokenSchema]
