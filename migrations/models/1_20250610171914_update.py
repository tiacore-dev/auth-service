from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "legal_entities";
        DROP TABLE IF EXISTS "legal_entity_types";
        DROP TABLE IF EXISTS "entity_company_relations";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ;"""
