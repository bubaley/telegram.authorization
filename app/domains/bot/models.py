from tortoise import fields

from app.core.encryption.crypto import CryptoManager
from app.core.models import BaseModel


class Bot(BaseModel):
    id = fields.CharField(primary_key=True, max_length=128)
    name = fields.CharField(max_length=255)
    username: str | None = fields.CharField(max_length=255, null=True)
    active = fields.BooleanField(default=False)
    token: str | None = fields.CharField(max_length=255, null=True)  # encrypted field
    secret_token = fields.CharField(max_length=512)  # encrypted field

    @property
    def decrypted_token(self) -> str | None:
        if not self.token:
            return None
        return CryptoManager.decrypt(self.token)

    @property
    def decrypted_secret_token(self) -> str | None:
        if not self.secret_token:
            return None
        return CryptoManager.decrypt(self.secret_token)
