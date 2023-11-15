import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import AiogramError
from aiogram.types import Update

from database import ObjectNotFoundError
from serial_services import ParsingError

admin_logger = logging.getLogger('admin')


class ErrorMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    async def __call__(self, handler: Callable[[Update, dict[str, Any]], Awaitable[Any]], event: Update,
                       data: dict[str, Any]) -> Any:
        user_id = data['event_from_user'].id if 'event_from_user' in data else None
        try:
            return await handler(event, data)
        except (ObjectNotFoundError, ParsingError) as e:
            admin_logger.exception(e)
            if user_id:
                await self.bot.send_message(user_id, f'Произошла ошибка, попробуйте позже. {e}')
        except AiogramError as e:
            admin_logger.exception(e)
            if user_id:
                await self.bot.send_message(user_id, 'Не удалось обработать запрос.')
        except BaseException as e:
            admin_logger.exception(e)
            if user_id:
                await self.bot.send_message(user_id, 'На сервере произошла ошибка.')
