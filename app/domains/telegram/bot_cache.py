import asyncio
from typing import Dict, Optional, Tuple

from aiogram import Bot as AiogramBot
from aiogram import Dispatcher
from loguru import logger

from app.domains.bot.models import Bot


class BotCache:
    """Cache for webhook bots to avoid recreating dispatcher and bot instances"""

    # Class variables for singleton pattern
    _instance: Optional['BotCache'] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self._cache: Dict[str, Tuple[AiogramBot, Dispatcher]] = {}
        self._cache_lock = asyncio.Lock()

    @classmethod
    async def _get_instance(cls) -> 'BotCache':
        """Get singleton instance"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @staticmethod
    async def get_or_create_bot(bot: Bot) -> Tuple[AiogramBot, Dispatcher]:
        cache = await BotCache._get_instance()
        """Get cached bot and dispatcher or create new ones"""
        async with cache._cache_lock:
            if bot.id in cache._cache:
                return cache._cache[bot.id]

            aiogram_bot = AiogramBot(token=bot.decrypted_token or '')
            dispatcher = Dispatcher()

            # Register event handlers
            from app.domains.telegram.event_handler import EventHandler

            EventHandler.register_handlers(dispatcher)

            cache._cache[bot.id] = (aiogram_bot, dispatcher)
            logger.info(f'Created cache for bot {bot.id}')
            return aiogram_bot, dispatcher

    @staticmethod
    async def clear_bot(bot: Bot) -> None:
        cache = await BotCache._get_instance()
        """Remove bot from cache and close session"""
        async with cache._cache_lock:
            if bot.id in cache._cache:
                aiogram_bot, dispatcher = cache._cache[bot.id]
                try:
                    await dispatcher.stop_polling()
                    logger.info(f'Stop polling for bot {bot.id}')
                except Exception:  # nosec B110
                    pass
                try:
                    await aiogram_bot.session.close()
                except Exception:  # nosec B110
                    pass

                del cache._cache[bot.id]
                logger.info(f'Cleared cache for bot {bot.id}')
