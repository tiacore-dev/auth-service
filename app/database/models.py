import uuid

import bcrypt
from tortoise import fields
from tortoise.models import Model


class Permission(Model):
    id = fields.CharField(max_length=255, pk=True)
    name = fields.CharField(max_length=255)
    comment = fields.CharField(max_length=255, null=True)

    def __repr__(self):
        return f"<Permissions(permission_id={self.id}, permission_name={self.name})>"

    class Meta:
        table = "permissions"


class Restriction(Model):
    id = fields.CharField(max_length=255, pk=True)
    name = fields.CharField(max_length=255)
    comment = fields.CharField(max_length=255, null=True)

    def __repr__(self):
        return f"<Restrictions(restriction_id={self.id}, restriction_name={self.name})>"

    class Meta:
        table = "restrictions"


class Application(Model):
    id = fields.CharField(pk=True, max_length=100)  # например: "crm_app"
    name = fields.CharField(max_length=255, unique=True)
    description = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "applications"

    def __repr__(self):
        return f"<Application(id={self.id}, name={self.name})>"


class ApiToken(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="api_tokens", on_delete=fields.CASCADE)
    application = fields.ForeignKeyField("models.Application", related_name="api_tokens", on_delete=fields.CASCADE)
    token_hash = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField(null=True)
    comment = fields.TextField(null=True)

    class Meta:
        table = "api_tokens"

    def __repr__(self):
        return f"""<ApiToken(id={self.id}, user_id={self.user.id}, 
        app={self.application.id})>"""


class Role(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=50, unique=True)
    system_name = fields.CharField(max_length=50, null=True)
    comment = fields.TextField(null=True)
    application_id = fields.CharField(max_length=100)

    def __repr__(self):
        return f"<Role(role_id={self.id}, role_name='{self.name}')>"

    class Meta:
        table = "user_roles"


class RoleIncludeRelation(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parent_role = fields.ForeignKeyField("models.Role", related_name="included_roles", on_delete=fields.CASCADE)
    child_role = fields.ForeignKeyField("models.Role", related_name="included_in_roles", on_delete=fields.CASCADE)

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "role_include_relations"


class RolePermissionRelation(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    role = fields.ForeignKeyField(
        "models.Role",
        related_name="role_permission_relations",
        on_delete=fields.CASCADE,
    )
    permission = fields.ForeignKeyField(
        "models.Permission",
        related_name="role_permission_relations",
        on_delete=fields.CASCADE,
    )
    restriction = fields.ForeignKeyField(
        "models.Restriction",
        related_name="role_permission_relations",
        null=True,
        on_delete=fields.SET_NULL,
    )

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "role_permission_relations"


class User(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=255)
    position = fields.CharField(max_length=255, null=True)
    is_superadmin = fields.BooleanField(default=False)
    is_verified = fields.BooleanField(default=False)
    company_subscriptions: fields.ReverseRelation["CompanySubscription"]

    class Meta:
        table = "users"

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def update_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @classmethod
    async def create_user(
        cls,
        email: str,
        password: str,
        full_name: str,
        position: str | None = None,
        is_superadmin: bool = False,
        is_verified: bool = False,
    ):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        return await cls.create(
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            position=position,
            is_superadmin=is_superadmin,
            is_verified=is_verified,
        )


class Company(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    company_subscriptions: fields.ReverseRelation["CompanySubscription"]

    class Meta:
        table = "companies"


class UserCompanyRelation(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    company = fields.ForeignKeyField(
        "models.Company",
        related_name="user_company_relations",
        on_delete=fields.CASCADE,
    )
    user = fields.ForeignKeyField("models.User", related_name="user_company_relations", on_delete=fields.CASCADE)
    role = fields.ForeignKeyField("models.Role", related_name="user_company_relations", on_delete=fields.CASCADE)
    application = fields.ForeignKeyField(
        "models.Application",
        related_name="roles",
        on_delete=fields.CASCADE,
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_to_company_relations"


class Subscription(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    price = fields.FloatField()
    application = fields.ForeignKeyField("models.Application", related_name="subscriptions")
    description = fields.TextField(null=True)
    comment = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()
    company_subscriptions: fields.ReverseRelation["CompanySubscription"]

    class Meta:
        table = "subscriptions"


class SubscriptionDetails(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    subscription = fields.ForeignKeyField("models.Subscription", related_name="subscription_details")
    entity_name = fields.CharField(max_length=255)
    bd_table = fields.CharField(max_length=100)
    restriction = fields.IntField()
    description = fields.TextField(null=True)
    comment = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "subscription_details"


class CompanySubscription(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    company = fields.ForeignKeyField("models.Company", related_name="company_subscriptions")
    subscription = fields.ForeignKeyField("models.Subscription", related_name="company_subscriptions")

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "company_subscriptions"
        unique_together = ("company", "subscription")


class SubscriptionPayments(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    company_subscription = fields.ForeignKeyField("models.CompanySubscription", related_name="payments")
    payment_external_id = fields.CharField(max_length=255, null=True)
    payment_date = fields.DateField()
    payment_amount = fields.FloatField()
    date_from = fields.DateField()
    date_to = fields.DateField()

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "subscription_payments"
