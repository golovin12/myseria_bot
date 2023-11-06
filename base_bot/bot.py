import abc
import logging
from typing import Any, Dict, Callable, Awaitable

import redis
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import Update

from consts import RedisDatabases
from database import ObjectNotFoundError
from serial_services import ParsingError
from .handlers import BaseHandler

logger = logging.getLogger(__name__)


class BaseBot(abc.ABC):

    def __init__(self, bot_token: str, skip_updates: bool, key: str, redis_host: str | None = None):
        self.skip_updates = skip_updates
        self.key = key
        self.bot = Bot(bot_token, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher(storage=self._get_fsm_storage(redis_host))
        self.dp.update.outer_middleware(self.errors_middleware)
        self.handlers = self._get_handlers()
        self.register_handlers_first()  # хандлеры, которые должны выполняться всегда (в основном - обработчики команд)
        self.register_handler_second()  # хандлеры, которые зависят от состояний

    def _get_fsm_storage(self, redis_host: str | None) -> RedisStorage | None:
        if redis_host:
            aioredis = redis.asyncio.Redis(host=redis_host, db=RedisDatabases.fsm_storage, decode_responses=True)
            return RedisStorage(aioredis, key_builder=DefaultKeyBuilder(prefix=f"fsm_{self.key}"))

    @abc.abstractmethod
    def _get_handlers(self) -> list[BaseHandler]:
        ...

    async def on_startapp(self, url: str, secret_token: str):
        await self.bot.set_webhook(f"{url}/bot/{self.key}", secret_token=secret_token,
                                   drop_pending_updates=self.skip_updates)

    async def on_shutdown(self):
        await self.bot.delete_webhook(self.skip_updates)
        await self.dp.storage.close()

    async def process_new_updates(self, data: dict[Any, Any]) -> None:
        update = Update.model_validate(data, context={"bot": self.bot})
        await self.dp.feed_update(self.bot, update)

    async def errors_middleware(self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
                                event: Update, data: Dict[str, Any]):
        try:
            return await handler(event, data)
        except (ObjectNotFoundError, ParsingError) as e:
            logger.exception(e)
            print(f'error event: {event}')
            await self.bot.send_message(data['event_from_user'].id, f'Произошла ошибка, попробуйте позже. {e}')
        except AiogramError as e:
            logger.exception(e)
            print(f'error event: {event}')
            await self.bot.send_message(data['event_from_user'].id, 'Не удалось обработать запрос.')

    def register_handlers_first(self):
        for handler in self.handlers:
            handler.register_first()

    def register_handler_second(self):
        for handler in self.handlers:
            handler.register_second()
