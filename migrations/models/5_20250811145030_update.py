from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
      
        ALTER TABLE "company_subscriptions" DROP COLUMN "user_id";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "company_subscriptions" ADD "user_id" UUIDNOT NULL;
        ALTER TABLE "company_subscriptions" ADD CONSTRAINT "fk_company__users" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;"""
