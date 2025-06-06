from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

from app.database.models import UserCompanyRelation


class RolePermissionBlock(BaseModel):
    role: str
    permissions: List[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    permissions: Optional[Dict[str, Dict[str, List[dict]]]] = None
    is_superadmin: bool
    user_id: UUID

    @model_validator(mode="after")
    def check_permissions_for_non_superadmin(self) -> "TokenResponse":
        if not self.is_superadmin:
            if self.permissions is not None:
                # Если есть компании, проверяем, что у них есть права
                if any(len(perms) == 0 for perms in self.permissions.values()):
                    raise ValueError(
                        "permissions must be provided if user is not a superadmin"
                    )
        return self


class UserCompanyRelationOut(BaseModel):
    id: UUID
    company_id: UUID
    role: str

    @classmethod
    def from_orm(cls, relation: UserCompanyRelation):
        return cls(
            id=relation.id, company_id=relation.company.id, role=relation.role.name
        )

    class Config:
        orm_mode = True


class MEResponse(BaseModel):
    user_id: UUID
    is_superadmin: bool
    email: str
    permissions: Optional[Dict[str, Dict[str, List[dict]]]] = None
    companies: List[UUID]
    relations: List[UserCompanyRelationOut]


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    position: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class RegisterResponse(BaseModel):
    user_id: UUID


class InviteRequest(BaseModel):
    email: str
    company_id: UUID
    role_id: UUID
    application_id: str
