from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "applications" (
    "id" VARCHAR(100) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "description" TEXT,
    "is_active" BOOL NOT NULL DEFAULT True
);
CREATE TABLE IF NOT EXISTS "companies" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT
);
CREATE TABLE IF NOT EXISTS "legal_entity_types" (
    "id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "legal_entities" (
    "id" UUID NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(255),
    "short_name" VARCHAR(255) NOT NULL,
    "inn" VARCHAR(12) NOT NULL,
    "kpp" VARCHAR(9),
    "ogrn" VARCHAR(13) NOT NULL UNIQUE,
    "vat_rate" INT NOT NULL DEFAULT 0,
    "address" VARCHAR(255),
    "opf" VARCHAR(255),
    "signer" VARCHAR(255),
    "entity_type_id" VARCHAR(255) REFERENCES "legal_entity_types" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_legal_entit_inn_06a077" UNIQUE ("inn", "kpp")
);
CREATE TABLE IF NOT EXISTS "entity_company_relations" (
    "id" UUID NOT NULL PRIMARY KEY,
    "relation_type" VARCHAR(10) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "company_id" UUID NOT NULL REFERENCES "companies" ("id") ON DELETE CASCADE,
    "legal_entity_id" UUID NOT NULL REFERENCES "legal_entities" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "permissions" (
    "id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "comment" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "restrictions" (
    "id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "comment" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "user_roles" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "system_name" VARCHAR(50) UNIQUE,
    "comment" TEXT
);
CREATE TABLE IF NOT EXISTS "role_permission_relations" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "application_id" VARCHAR(100) NOT NULL REFERENCES "applications" ("id") ON DELETE CASCADE,
    "permission_id" VARCHAR(255) NOT NULL REFERENCES "permissions" ("id") ON DELETE CASCADE,
    "restriction_id" VARCHAR(255) REFERENCES "restrictions" ("id") ON DELETE SET NULL,
    "role_id" UUID NOT NULL REFERENCES "user_roles" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "full_name" VARCHAR(255) NOT NULL,
    "position" VARCHAR(255),
    "is_superadmin" BOOL NOT NULL DEFAULT False,
    "is_verified" BOOL NOT NULL DEFAULT False
);
CREATE TABLE IF NOT EXISTS "api_tokens" (
    "id" UUID NOT NULL PRIMARY KEY,
    "token_hash" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMPTZ,
    "comment" TEXT,
    "application_id" VARCHAR(100) NOT NULL REFERENCES "applications" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_to_company_relations" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "company_id" UUID NOT NULL REFERENCES "companies" ("id") ON DELETE CASCADE,
    "role_id" UUID NOT NULL REFERENCES "user_roles" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
