from fastapi import FastAPI

from .application_route import application_router
from .auth_route import auth_router
from .company_route import company_router
from .company_subscription_route import company_subscription_router
from .include_roles_route import role_include_router
from .invite_route import invite_router
from .permissions_route import permissions_router
from .register_route import register_router
from .reset_password_route import reset_router
from .restrictions_route import restrictions_router
from .role_permission_relation_route import role_relation_router
from .role_route import role_router
from .subscription_details_route import subscription_details_router
from .subscription_payments_route import subscription_payment_router
from .subscription_route import subscription_router
from .user_company_relation_route import relation_router
from .user_route import user_router


def register_routes(app: FastAPI):
    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(register_router, prefix="/api", tags=["Register"])
    app.include_router(invite_router, prefix="/api", tags=["Invite"])
    app.include_router(reset_router, prefix="/api", tags=["ResetPassword"])
    app.include_router(user_router, prefix="/api/users", tags=["Users"])
    app.include_router(company_router, prefix="/api/companies", tags=["Companies"])
    app.include_router(
        relation_router,
        prefix="/api/user-company-relations",
        tags=["UserCompanyRelations"],
    )

    app.include_router(role_router, prefix="/api/roles", tags=["Roles"])
    app.include_router(role_include_router, prefix="/api/include-roles", tags=["IncludeRoles"])
    app.include_router(permissions_router, prefix="/api/permissions", tags=["Permissions"])
    app.include_router(restrictions_router, prefix="/api/restrictions", tags=["Restrictions"])
    app.include_router(
        role_relation_router,
        prefix="/api/role-permission-relations",
        tags=["RolePermissionRelations"],
    )

    app.include_router(application_router, prefix="/api/applications", tags=["Applications"])
    app.include_router(subscription_router, prefix="/api/subscriptions", tags=["Subscriptions"])
    app.include_router(subscription_details_router, prefix="/api/subscription-details", tags=["SubscriptionDetails"])
    app.include_router(company_subscription_router, prefix="/api/company-subscriptions", tags=["CompanySubscriptions"])
    app.include_router(subscription_payment_router, prefix="/api/subscription-payments", tags=["SubscriptionPayments"])
