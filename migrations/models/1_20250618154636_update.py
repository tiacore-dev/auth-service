from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_roles" ADD COLUMN "application_id" VARCHAR(100);
        INSERT INTO "applications" (id, name) VALUES ('auth_app', 'Auth service') ON CONFLICT (id) DO NOTHING;
        UPDATE "user_roles" SET "application_id" = 'auth_app';
        ALTER TABLE "user_roles" ALTER COLUMN "application_id" SET NOT NULL;
        ALTER TABLE "user_roles" ADD CONSTRAINT "user_roles_application_id_fkey"
            FOREIGN KEY ("application_id") REFERENCES "applications" ("id") ON DELETE CASCADE;

        ALTER TABLE "role_permission_relations" DROP CONSTRAINT IF EXISTS "role_permission_relations_application_id_fkey";
        ALTER TABLE "role_permission_relations" DROP COLUMN IF EXISTS "application_id";

        ALTER TABLE "user_to_company_relations" ADD COLUMN "application_id" VARCHAR(100);
        UPDATE "user_to_company_relations" SET "application_id" = 'auth_app';
        ALTER TABLE "user_to_company_relations" ALTER COLUMN "application_id" SET NOT NULL;
        ALTER TABLE "user_to_company_relations" ADD CONSTRAINT "user_to_company_relations_application_id_fkey"
            FOREIGN KEY ("application_id") REFERENCES "applications" ("id") ON DELETE CASCADE;

        DROP TABLE IF EXISTS "legal_entities" CASCADE;
        DROP TABLE IF EXISTS "legal_entity_types" CASCADE;
        DROP TABLE IF EXISTS "entity_company_relations" CASCADE;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_to_company_relations" DROP CONSTRAINT IF EXISTS "user_to_company_relations_application_id_fkey";
        ALTER TABLE "user_roles" DROP COLUMN IF EXISTS "application_id";
        ALTER TABLE "user_to_company_relations" DROP COLUMN IF EXISTS "application_id";
        ALTER TABLE "role_permission_relations" ADD COLUMN IF NOT EXISTS "application_id" VARCHAR(100) NOT NULL;
        ALTER TABLE "role_permission_relations" ADD CONSTRAINT IF NOT EXISTS "role_permission_relations_application_id_fkey"
            FOREIGN KEY ("application_id") REFERENCES "applications" ("id") ON DELETE CASCADE;
    """
