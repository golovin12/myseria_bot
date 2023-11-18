import logging
from typing import Type

from .controller import UserController
from .handlers import handler_classes, UserHandler
from .keyboards import get_menu_commands
from bots.base_bot import BaseBot

admin_logger = logging.getLogger('admin')


class UserBot(BaseBot):
    controller: Type[UserController]

    def _get_handlers(self) -> list[UserHandler]:
        return [handler(self.dp, self.controller) for handler in handler_classes]

    async def on_startapp(self, url: str, secret_token: str, cert_path: str | None = None):
        await super().on_startapp(url, secret_token, cert_path)
        await self.bot.set_my_commands(get_menu_commands())
        admin_logger.info(f'Бот {self.name} запущен.')

    async def on_shutdown(self):
        admin_logger.info(f'Бот {self.name} остановлен.')
        await super().on_shutdown()
