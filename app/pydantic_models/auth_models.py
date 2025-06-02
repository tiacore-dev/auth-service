from typing import Dict, List, Optional

from pydantic import UUID4, BaseModel, model_validator


class RolePermissionBlock(BaseModel):
    role: str
    permissions: List[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    permissions: Optional[Dict[str, Dict[str, List[dict]]]] = None
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


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    position: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class RegisterResponse(BaseModel):
    user_id: UUID4


class InviteRequest(BaseModel):
    email: str
    company_id: UUID4
    role_id: UUID4
    application_id: str
