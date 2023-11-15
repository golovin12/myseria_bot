import abc
from typing import Any

import redis
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import Update

from consts import RedisDatabases
from .handlers import BaseHandler
from .middlewares import ErrorMiddleware


class BaseBot(abc.ABC):

    def __init__(self, name, bot_token: str, skip_updates: bool, key: str, redis_host: str | None = None):
        self.name = name
        self.skip_updates = skip_updates
        self.key = key
        self.bot = Bot(bot_token, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher(storage=self._get_fsm_storage(redis_host))
        self._register_middlewares()
        self.handlers = self._get_handlers()
        self._register_handlers_first()
        self._register_handler_second()

    def _get_fsm_storage(self, redis_host: str | None) -> RedisStorage | None:
        if redis_host:
            aioredis = redis.asyncio.Redis(host=redis_host, db=RedisDatabases.fsm_storage, decode_responses=True)
            return RedisStorage(aioredis, key_builder=DefaultKeyBuilder(prefix=f"fsm_{self.key}"))

    @abc.abstractmethod
    def _get_handlers(self) -> list[BaseHandler]:
        """Возвращает список хандлеров для бота"""
        ...

    def _register_middlewares(self):
        """Регистрация middlewares"""
        self.dp.update.outer_middleware(ErrorMiddleware(self.bot))

    def _register_handlers_first(self):
        """Регистрация хандлерор, которые должны выполняться всегда (в основном - обработчики команд)"""
        for handler in self.handlers:
            handler.register_first()

    def _register_handler_second(self):
        """Регистрация хандлеров, которые зависят от состояний"""
        for handler in self.handlers:
            handler.register_second()

    async def on_startapp(self, url: str, secret_token: str):
        await self.bot.set_webhook(f"{url}/bot/{self.key}", secret_token=secret_token,
                                   drop_pending_updates=self.skip_updates)

    async def on_shutdown(self):
        await self.bot.delete_webhook(self.skip_updates)
        await self.dp.storage.close()

    async def process_new_updates(self, data: dict[str, Any]) -> None:
        update = Update.model_validate(data, context={"bot": self.bot})
        await self.dp.feed_update(self.bot, update)
