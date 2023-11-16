import dramatiq
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from config import settings


@dramatiq.actor(queue_name='admin')
async def admin_bot_send_message(user_id: int, message: str):
    async with AiohttpSession() as session:
        bot = Bot(settings.ADMIN_BOT_TOKEN, session=session, parse_mode=ParseMode.HTML)
        await bot.send_message(user_id, message)
