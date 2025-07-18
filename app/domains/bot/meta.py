from fastapi_mason.schemas import SchemaMeta

from app.core.models import BASE_FIELDS


class BotMeta(SchemaMeta):
    include = (
        *BASE_FIELDS,
        'name',
        'active',
        'username',
    )


class BotCreateMeta(SchemaMeta):
    include = (
        'id',
        'name',
        'token',
    )
