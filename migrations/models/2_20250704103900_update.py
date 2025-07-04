from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_roles" DROP CONSTRAINT IF EXISTS "user_roles_system_name_key";
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "user_roles_system_name_key" ON "user_roles" ("system_name");"""
