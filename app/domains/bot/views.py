from fastapi import APIRouter
from fastapi_mason.decorators import action, viewset
from fastapi_mason.lookups import build_lookup_class
from fastapi_mason.mixins import ListMixin
from fastapi_mason.wrappers import ResponseDataWrapper

from app.core.viewsets import BaseGenericViewSet
from app.domains.bot.models import Bot
from app.domains.bot.schemas import BotCreateSchema, BotInfoSchema, BotReadSchema
from app.domains.bot.services.bot_service import BotService

bots_router = APIRouter(prefix='/bots', tags=['bots'])


@viewset(bots_router)
class BotViewSet(BaseGenericViewSet[Bot], ListMixin[Bot]):
    model = Bot
    read_schema = BotReadSchema
    create_schema = BotCreateSchema
    lookup_class = build_lookup_class('BotLookup', 'bot_id', str)

    @action(methods=['POST'], detail=False, summary='Setup bot', response_model=ResponseDataWrapper[BotReadSchema])
    async def setup(self, data: BotCreateSchema):
        bot = await BotService.setup_bot(data)
        result = await BotReadSchema.from_tortoise_orm(bot)
        return ResponseDataWrapper.wrap(result)

    @action(methods=['GET'], detail=True, summary='Bot info', response_model=ResponseDataWrapper[BotInfoSchema])
    async def info(self, bot_id: str):
        bot = await self.get_object(bot_id)
        return ResponseDataWrapper.wrap(await BotService.get_bot_info(bot))

    @action(methods=['PUT'], detail=True, summary='Deactivate bot', response_model=ResponseDataWrapper[BotReadSchema])
    async def deactivate(self, bot_id: str):
        bot = await self.get_object(bot_id)
        await BotService.deactivate_bot(bot)
        result = await BotReadSchema.from_tortoise_orm(bot)
        return ResponseDataWrapper.wrap(result)
