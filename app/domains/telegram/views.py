from aiogram.types import Update
from fastapi import APIRouter, HTTPException, Request

from app.domains.bot.models import Bot
from app.domains.telegram.bot_cache import BotCache

telegram_router = APIRouter()


@telegram_router.post('/bots/webhook/{bot_id}', summary='Telegram webhook endpoint', tags=['bots'])
async def telegram_webhook(bot_id: str, request: Request):
    """Handle incoming telegram webhooks"""
    bot = await Bot.get_or_none(id=bot_id, active=True)
    success_data = {'status': 'ok'}
    if not bot:
        return success_data
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != bot.decrypted_secret_token:
        return success_data
    try:
        update_data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid JSON data')
    update = Update.model_validate(update_data, from_attributes=True)

    aiogram_bot, dp = await BotCache.get_or_create_bot(bot)
    await dp.feed_webhook_update(aiogram_bot, update)

    return success_data
