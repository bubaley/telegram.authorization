from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "bot" (
    "id" VARCHAR(128) NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "username" VARCHAR(255),
    "active" BOOL NOT NULL DEFAULT False,
    "token" VARCHAR(255),
    "secret_token" VARCHAR(512) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_bot_created_faf285" ON "bot" ("created_at");
CREATE TABLE IF NOT EXISTS "link" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" VARCHAR(128) NOT NULL,
    "auth_type" VARCHAR(255) NOT NULL DEFAULT 'simple',
    "webhook_url" VARCHAR(512),
    "key" VARCHAR(512),
    "used_at" TIMESTAMPTZ,
    "telegram_user_id" INT,
    "username" VARCHAR(255),
    "phone" VARCHAR(255),
    "duration" INT NOT NULL DEFAULT 300,
    "expire_at" TIMESTAMPTZ NOT NULL,
    "auth_link" VARCHAR(255),
    "bot_id" VARCHAR(128) NOT NULL REFERENCES "bot" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_link_created_15e60b" ON "link" ("created_at");
COMMENT ON COLUMN "link"."auth_type" IS 'SIMPLE: simple\nPHONE: phone';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
