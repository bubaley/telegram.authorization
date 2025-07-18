from enum import Enum
from uuid import uuid4

from tortoise import fields

from app.core.encryption.crypto import CryptoManager
from app.core.models import BaseModel
from app.domains.bot.models import Bot


class AuthType(str, Enum):
    SIMPLE = 'simple'
    PHONE = 'phone'


class Link(BaseModel):
    id = fields.UUIDField(primary_key=True, default=uuid4)
    bot: fields.ForeignKeyRelation[Bot] = fields.ForeignKeyField('models.Bot', related_name='links')
    bot_id: str | None

    user_id = fields.CharField(max_length=128)
    auth_type = fields.CharEnumField(enum_type=AuthType, max_length=255, default=AuthType.SIMPLE)
    webhook_url = fields.CharField(max_length=512, null=True)
    key: str | None = fields.CharField(max_length=512, null=True)  # encrypted field

    used_at = fields.DatetimeField(null=True)
    telegram_user_id = fields.IntField(null=True)
    username: str | None = fields.CharField(max_length=255, null=True)
    phone = fields.CharField(max_length=255, null=True)
    duration = fields.IntField(default=60 * 5)
    expire_at = fields.DatetimeField()
    auth_link = fields.CharField(max_length=255, null=True)

    class Meta:
        ordering = ('-created_at',)

    @property
    def decrypted_key(self) -> str | None:
        if not self.key:
            return None
        return CryptoManager.decrypt(self.key)
