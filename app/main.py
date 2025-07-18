from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.core.auth import verify_token
from app.core.database import register_database
from app.core.settings import settings
from app.domains.bot.models import Bot
from app.domains.bot.views import bots_router
from app.domains.link.views import links_router
from app.domains.telegram.polling_manager import PollingManager
from app.domains.telegram.views import telegram_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    bot: Bot | None = None
    if settings.debug and settings.debug_bot_id:
        bot = await Bot.filter(id=settings.debug_bot_id, active=True).first()
    if bot:
        try:
            await PollingManager.start_debug_polling(bot)
            yield
        except Exception:
            yield
        finally:
            await PollingManager.stop_debug_polling()
    else:
        yield


app = FastAPI(
    title='Telegram authorization service',
    version='0.0.0',
    lifespan=lifespan,
)
register_database(app)

app.include_router(bots_router, dependencies=[Depends(verify_token)])
app.include_router(links_router, dependencies=[Depends(verify_token)])
app.include_router(telegram_router)


@app.get('/health')
async def health():
    return {'status': 'ok'}
