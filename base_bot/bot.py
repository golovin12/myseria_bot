import abc
from typing import Any

import redis
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import Update

from .handler import BaseHandler
from .handler_errors import ErrorsHandler


class BaseBot(abc.ABC):

    def __init__(self, bot_token: str, skip_updates: bool, key: str, redis_host: str | None = None):
        self.skip_updates = skip_updates
        self.key = key
        self.bot = Bot(bot_token, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher(storage=self._get_fsm_storage(redis_host))
        self.handlers = self._get_handlers()
        self.register_handlers_first()  # хандлеры, которые должны выполняться всегда (в основном - обработчики команд)
        self.register_handler_second()  # хандлеры, которые зависят от состояний

    def _get_fsm_storage(self, redis_host: str | None) -> RedisStorage | None:
        if redis_host:
            return RedisStorage(redis.asyncio.Redis(host=redis_host, db=2, decode_responses=True),
                                key_builder=DefaultKeyBuilder(prefix=f"fsm_{self.key}"))

    def _get_handlers(self) -> list[BaseHandler]:
        return [ErrorsHandler(self.dp)]

    async def on_startapp(self, url: str, secret_token: str):
        await self.bot.set_webhook(f"{url}/bot/{self.key}", secret_token=secret_token,
                                   drop_pending_updates=self.skip_updates)

    async def on_shutdown(self):
        await self.bot.delete_webhook(self.skip_updates)
        await self.dp.storage.close()

    async def process_new_updates(self, data: dict[Any, Any]) -> None:
        update = Update.model_validate(data, context={"bot": self.bot})
        await self.dp.feed_update(self.bot, update)

    def register_handlers_first(self):
        for handler in self.handlers:
            handler.register_first()

    def register_handler_second(self):
        for handler in self.handlers:
            handler.register_second()
