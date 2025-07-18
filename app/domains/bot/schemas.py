from typing import TYPE_CHECKING

from aiogram.types import User, WebhookInfo
from fastapi_mason.schemas import build_schema
from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel

from app.domains.bot.meta import BotCreateMeta, BotMeta
from app.domains.bot.models import Bot

BotReadSchema = build_schema(Bot, meta=BotMeta)
BotCreateSchema = build_schema(Bot, meta=BotCreateMeta)


if TYPE_CHECKING:
    BotCreateSchema = type('BotCreateSchema', (Bot, PydanticModel), {})
    BotReadSchema = type('BotReadSchema', (Bot, PydanticModel), {})


class BotInfoSchema(BaseModel):
    is_debug_bot: bool
    bot: BotReadSchema
    telegram_bot: User
    webhook: WebhookInfo
