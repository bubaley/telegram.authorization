from aiogram import Bot as AiogramBot
from aiogram.exceptions import AiogramError
from fastapi import HTTPException
from loguru import logger

from app.core.settings import settings
from app.domains.bot.models import Bot
from app.domains.telegram.bot_cache import BotCache


class WebhookManager:
    """Manager for Telegram webhook operations"""

    @staticmethod
    async def setup_webhook(bot: Bot):
        """Setup webhook for telegram bot"""
        if not settings.base_url:
            raise HTTPException(status_code=400, detail='Webhook URL not configured')

        try:
            aiogram_bot = AiogramBot(token=bot.decrypted_token or '')
            webhook_url = f'{settings.base_url.rstrip("/")}/bots/webhook/{bot.id}'
            await aiogram_bot.set_webhook(url=webhook_url, secret_token=bot.decrypted_secret_token)
            await aiogram_bot.session.close()
            logger.info(f'Webhook setup for bot {bot.id}: {webhook_url}')

            # Invalidate cache for this bot since token might have changed
            await BotCache.clear_bot(bot)

        except AiogramError as e:
            raise HTTPException(status_code=400, detail=f'Failed to setup webhook: {str(e)}')

    @staticmethod
    async def delete_webhook(bot: Bot):
        """Delete webhook for telegram bot (used for long polling mode)"""
        try:
            aiogram_bot = AiogramBot(token=bot.decrypted_token or '')
            await aiogram_bot.delete_webhook(drop_pending_updates=True)
            await aiogram_bot.session.close()
            logger.info('Webhook deleted')

            # Invalidate cache for this bot
            await BotCache.clear_bot(bot)

        except AiogramError as e:
            raise HTTPException(status_code=400, detail=f'Failed to delete webhook: {str(e)}')

    @staticmethod
    async def get_webhook_info(bot: Bot):
        """Get current webhook information"""
        try:
            aiogram_bot = AiogramBot(token=bot.decrypted_token or '')
            webhook_info = await aiogram_bot.get_webhook_info()
            await aiogram_bot.session.close()
            return webhook_info
        except AiogramError as e:
            raise HTTPException(status_code=400, detail=f'Failed to get webhook info: {str(e)}')
