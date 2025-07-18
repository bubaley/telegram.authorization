from fastapi_mason.schemas import SchemaMeta

from app.core.models import BASE_FIELDS


class LinkMeta(SchemaMeta):
    include = (
        *BASE_FIELDS,
        'bot_id',
        'user_id',
        'auth_type',
        'webhook_url',
        'duration',
        'expire_at',
        'used_at',
        'telegram_user_id',
        'username',
        'phone',
        'auth_link',
    )


class LinkCreateMeta(SchemaMeta):
    include = (
        *BASE_FIELDS,
        'bot',
        'bot_id',
        'user_id',
        'auth_type',
        'webhook_url',
        'key',
        'duration',
    )
