from uuid import uuid4

from aiogram.exceptions import AiogramError
from fastapi import HTTPException

from app.core.encryption.crypto import CryptoManager
from app.core.settings import settings
from app.domains.bot.models import Bot
from app.domains.bot.schemas import BotCreateSchema, BotInfoSchema, BotReadSchema
from app.domains.telegram.bot_manager import BotManager
from app.domains.telegram.polling_manager import PollingManager
from app.domains.telegram.webhook_manager import WebhookManager


class BotService:
    @staticmethod
    async def setup_bot(data: BotCreateSchema):
        dict_data = data.model_dump(exclude_unset=True)
        pk = dict_data.pop('id')
        token = dict_data.pop('token', None)
        dict_data['secret_token'] = CryptoManager.encrypt(str(uuid4()))
        bot, _ = await Bot.update_or_create(id=pk, defaults=dict_data)

        if token:
            try:
                bot_info = await BotManager.get_me(token)
                bot.token = CryptoManager.encrypt(token)

                if await BotService.is_debug_bot(pk):
                    await WebhookManager.delete_webhook(bot)
                    await PollingManager.start_debug_polling(bot)
                else:
                    await WebhookManager.setup_webhook(bot)
            except AiogramError as e:
                raise HTTPException(status_code=400, detail=str(e))

            bot.username = bot_info.username or None
            bot.active = True
            await bot.save()

        return bot

    @staticmethod
    async def is_debug_bot(bot_id: str) -> bool:
        return settings.debug_bot_id == bot_id

    @staticmethod
    async def get_bot_info(bot: Bot):
        try:
            bot_info = await BotManager.get_me(bot.decrypted_token or '')
            webhook_info = await WebhookManager.get_webhook_info(bot)
            schema_data = await BotReadSchema.from_tortoise_orm(bot)
            return BotInfoSchema(
                is_debug_bot=await BotService.is_debug_bot(bot.id),
                bot=schema_data,
                telegram_bot=bot_info,
                webhook=webhook_info,
            )
        except AiogramError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def deactivate_bot(bot: Bot):
        bot.active = False
        await bot.save()
        await WebhookManager.delete_webhook(bot)
        await PollingManager.stop_debug_polling()
        return bot
