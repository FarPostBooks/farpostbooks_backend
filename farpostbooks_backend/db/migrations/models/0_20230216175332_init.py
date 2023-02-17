from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "bookmodel" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(128) NOT NULL,
    "description" VARCHAR(1024) NOT NULL,
    "image" VARCHAR(64) NOT NULL,
    "author" VARCHAR(255) NOT NULL,
    "publish" VARCHAR(16) NOT NULL,
    "added_timestamp" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "bookmodel" IS 'Модель для таблицы с книгами.';
CREATE TABLE IF NOT EXISTS "usermodel" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(16) NOT NULL  DEFAULT 'user',
    "name" VARCHAR(64) NOT NULL,
    "position" VARCHAR(64) NOT NULL,
    "about" VARCHAR(255) NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "usermodel" IS 'Модель для таблицы с юзерами.';
CREATE TABLE IF NOT EXISTS "userbookmodel" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "get_timestamp" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "back_timestamp" TIMESTAMPTZ,
    "rating" SMALLINT,
    "book_id" BIGINT NOT NULL REFERENCES "bookmodel" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "userbookmodel" IS 'Модель для таблицы с книгами, которые были у юзеров.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
