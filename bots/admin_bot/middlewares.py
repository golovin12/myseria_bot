from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.types import Update

from database.models import Admin


class AdminOnlyMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    async def __call__(self, handler: Callable[[Update, dict[str, Any]], Awaitable[Any]], event: Update,
                       data: dict[str, Any]) -> Any:
        user_id = data['event_from_user'].id if 'event_from_user' in data else None
        admin = await Admin.get_object_or_none(user_id)
        if admin is not None and admin.is_admin:
            return await handler(event, data)
        await self.bot.send_message(user_id, 'Отказано в доступе.')
