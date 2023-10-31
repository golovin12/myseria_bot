from typing import Type

from .controller import UserController
from .handlers import handler_classes, UserHandler
from .keyboards import get_menu_commands
from base_bot import BaseBot, BaseHandler


class UserBot(BaseBot):
    controller: Type[UserController]

    def _get_handlers(self) -> list[BaseHandler | UserHandler]:
        handlers = super()._get_handlers()
        handlers.extend(handler(self.dp, self.controller) for handler in handler_classes)
        return handlers

    async def on_startapp(self, url: str, secret_token: str):
        await super().on_startapp(url, secret_token)
        await self.bot.set_my_commands(get_menu_commands())
