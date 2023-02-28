from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """ALTER TABLE "bookmodel" ALTER COLUMN "description" TYPE TEXT USING "description"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """ALTER TABLE "bookmodel" ALTER COLUMN "description" TYPE VARCHAR(1024) USING "description"::VARCHAR(1024);"""
