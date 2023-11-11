from typing import Type

from .controller import UserController
from .handlers import handler_classes, UserHandler
from .keyboards import get_menu_commands
from bots.base_bot import BaseBot


class UserBot(BaseBot):
    controller: Type[UserController]

    def _get_handlers(self) -> list[UserHandler]:
        return [handler(self.dp, self.controller) for handler in handler_classes]

    async def on_startapp(self, url: str, secret_token: str):
        await super().on_startapp(url, secret_token)
        await self.bot.set_my_commands(get_menu_commands())
