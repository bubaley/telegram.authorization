from datetime import datetime

from aiogram import Dispatcher
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from loguru import logger

from app.domains.link.models import AuthType, Link
from app.domains.link.orm.get_links import get_active_links
from app.domains.link.schemas import LinkReadSchema
from app.domains.telegram.messages import Messages


class EventHandler:
    """Handler for Telegram events and authorization flow"""

    @staticmethod
    def register_handlers(dp: Dispatcher):
        """Register all event handlers"""
        _ = dp.message.register(EventHandler.handle_start_command, CommandStart())
        _ = dp.message.register(EventHandler.handle_text_message)

    @staticmethod
    async def handle_start_command(message: Message, command: CommandObject):
        command = command.args
        if not command:
            return
        link = await get_active_links().filter(id=command).first()
        if not link or not message.from_user:
            _ = await message.answer(Messages.EXPIRED_LINK_MESSAGE)
            return
        link.username = message.from_user.username
        link.telegram_user_id = message.from_user.id
        await link.save()

        if link.auth_type == AuthType.PHONE:
            await EventHandler.request_contact(message, link)
        else:
            await EventHandler.complete_authorization(message, link)

    @staticmethod
    async def handle_text_message(message: Message):
        if message.contact and message.from_user:
            link = (
                await get_active_links().filter(telegram_user_id=message.from_user.id, auth_type=AuthType.PHONE).first()
            )
            if link:
                link.phone = message.contact.phone_number
                await link.save()
                await EventHandler.complete_authorization(message, link)

    @staticmethod
    async def request_contact(message: Message, link: Link):
        """Request phone contact from user"""
        if not message.from_user:
            return
        try:
            keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=Messages.SHARE_CONTACT_BUTTON, request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
            _ = await message.answer(Messages.SHARE_CONTACT_MESSAGE, reply_markup=keyboard)
            logger.info(f'Contact requested for link {link.id}, user {message.from_user.id}')
        except Exception as e:
            logger.error(f'Error requesting contact for link {link.id}: {e}')
            _ = await message.answer(Messages.UNHANDLED_ERROR_MESSAGE)

    @staticmethod
    async def complete_authorization(message: Message, link: Link):
        """Complete authorization and mark link as used"""
        if not message.from_user:
            return
        await link.save()
        link.used_at = datetime.now()
        try:
            if link.webhook_url:
                await EventHandler.send_webhook_notification(link)
            logger.info(f'Authorization completed for link {link.id}, user {message.from_user.id}')
        except Exception as e:
            logger.error(f'Error completing authorization for link {link.id}: {e}')
            await message.answer(Messages.WEBHOOK_NOTIFICATION_FAILED_MESSAGE, reply_markup=ReplyKeyboardRemove())
            return
        await message.answer(Messages.AUTHORIZATION_COMPLETED_MESSAGE, reply_markup=ReplyKeyboardRemove())

    @staticmethod
    async def send_webhook_notification(link: Link):
        """Send webhook notification about completed authorization"""
        try:
            import httpx

            schema_data = await LinkReadSchema.from_tortoise_orm(link)
            payload = schema_data.model_dump(mode='json')
            payload['key'] = link.decrypted_key

            async with httpx.AsyncClient() as client:
                response = await client.post(link.webhook_url, json=payload, timeout=5.0)
                response.raise_for_status()

            logger.info(f'Webhook notification sent for link {link.id}')

        except Exception as e:
            logger.error(f'Error sending webhook notification for link {link.id}: {e}')
            raise e
