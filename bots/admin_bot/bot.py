from .controller import AdminController
from .handlers import handler_classes, AdminHandler
from bots.base_bot import BaseBot


class AdminBot(BaseBot):
    controller = AdminController

    def _get_handlers(self) -> list[AdminHandler]:
        return [handler(self.dp, self.controller) for handler in handler_classes]
