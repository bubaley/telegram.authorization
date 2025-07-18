from uuid import uuid4

from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    id = fields.UUIDField(primary_key=True, default=uuid4)
    created_at = fields.DatetimeField(auto_now_add=True, db_index=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


BASE_FIELDS = ('id', 'created_at', 'updated_at')
