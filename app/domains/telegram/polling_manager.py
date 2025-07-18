import asyncio
from typing import Optional

from loguru import logger

from app.domains.bot.models import Bot
from app.domains.telegram.bot_cache import BotCache
from app.domains.telegram.webhook_manager import WebhookManager


class PollingManager:
    """Manager for Telegram long polling operations"""

    _polling_task: Optional[asyncio.Task] = None
    _current_bot: Bot | None = None

    @staticmethod
    async def start_debug_polling(bot: Bot):
        """Start long polling for debug bot if configured"""
        await PollingManager.stop_debug_polling()
        await WebhookManager.delete_webhook(bot)

        try:
            PollingManager._current_bot = bot
            aiogram_bot, dispatcher = await BotCache.get_or_create_bot(bot)

            PollingManager._polling_task = asyncio.create_task(
                dispatcher.start_polling(aiogram_bot, skip_updates=True, handle_signals=False)
            )
            logger.info(f'Started long polling for bot {bot.id}')

        except Exception as e:
            logger.error(f'Failed to start long polling: {e}')
            await PollingManager.stop_debug_polling()  # Cleanup on error

    @staticmethod
    async def stop_debug_polling():
        """Stop long polling for debug bot"""
        try:
            # Stop polling task
            if PollingManager._polling_task and not PollingManager._polling_task.done():
                PollingManager._polling_task.cancel()
            if not PollingManager._current_bot:
                return
            await BotCache.clear_bot(PollingManager._current_bot)
        except Exception as e:
            logger.error(f'Error during polling cleanup: {e}')
        finally:
            PollingManager._polling_task = None
            PollingManager._current_bot = None
