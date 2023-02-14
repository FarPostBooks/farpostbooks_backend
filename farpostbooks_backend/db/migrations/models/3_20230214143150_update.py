from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usermodel" ALTER COLUMN "name" TYPE VARCHAR(64) USING "name"::VARCHAR(64);
        ALTER TABLE "usermodel" ALTER COLUMN "position" TYPE VARCHAR(64) USING "position"::VARCHAR(64);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usermodel" ALTER COLUMN "name" TYPE VARCHAR(32) USING "name"::VARCHAR(32);
        ALTER TABLE "usermodel" ALTER COLUMN "position" TYPE VARCHAR(32) USING "position"::VARCHAR(32);"""
