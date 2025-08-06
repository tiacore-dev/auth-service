from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
     CREATE TABLE IF NOT EXISTS "subscriptions" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "price" DOUBLE PRECISION NOT NULL,
    "description" TEXT,
    "comment" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "application_id" VARCHAR(100) NOT NULL REFERENCES "applications" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "company_subscriptions" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "company_id" UUID NOT NULL REFERENCES "companies" ("id") ON DELETE CASCADE,
    "subscription_id" UUID NOT NULL REFERENCES "subscriptions" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_company_sub_company_76cb2a" UNIQUE ("company_id", "subscription_id")
);
       
        CREATE TABLE IF NOT EXISTS "subscription_details" (
    "id" UUID NOT NULL PRIMARY KEY,
    "entity_name" VARCHAR(255) NOT NULL,
    "bd_table" VARCHAR(100) NOT NULL,
    "restriction" INT NOT NULL,
    "description" TEXT,
    "comment" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "subscription_id" UUID NOT NULL REFERENCES "subscriptions" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "subscription_payments" (
    "id" UUID NOT NULL PRIMARY KEY,
    "payment_external_id" VARCHAR(255),
    "payment_date" DATE NOT NULL,
    "payment_amount" DOUBLE PRECISION NOT NULL,
    "date_from" DATE NOT NULL,
    "date_to" DATE NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "company_subscription_id" UUID NOT NULL REFERENCES "company_subscriptions" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "company_subscriptions";
        DROP TABLE IF EXISTS "subscriptions";
        DROP TABLE IF EXISTS "subscription_details";
        DROP TABLE IF EXISTS "subscription_payments";"""
