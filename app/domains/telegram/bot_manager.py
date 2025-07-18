from aiogram import Bot as AiogramBot
from aiogram.types import User as AiogramUser


class BotManager:
    """Manager for Telegram bot operations and state management"""

    @staticmethod
    async def get_me(token: str) -> AiogramUser:
        """Validate telegram bot token and return bot info"""
        aiogram_bot = AiogramBot(token=token)
        bot_info = await aiogram_bot.get_me()
        await aiogram_bot.session.close()
        return bot_info
