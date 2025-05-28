from typing import Dict, List, Optional

from pydantic import UUID4, BaseModel, Field, model_validator


class RolePermissionBlock(BaseModel):
    role: str
    permissions: List[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    permissions: Optional[Dict[str, List[RolePermissionBlock]]] = None
    is_superadmin: bool
    user_id: UUID4

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


class LoginRequest(BaseModel):
    email: str
    password: str
    application_id: str = Field(..., alias="application_id")


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    position: Optional[str] = None
    application_id: str


class RefreshRequest(BaseModel):
    refresh_token: str
    application_id: str


class RegisterResponse(BaseModel):
    user_id: UUID4


class InviteRequest(BaseModel):
    email: str
    company_id: UUID4
    role_id: UUID4
    application_id: str
