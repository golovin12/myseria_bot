from .controller import AdminController
from .handlers import handler_classes, AdminHandler
from base_bot import BaseHandler, BaseBot


class AdminBot(BaseBot):
    controller = AdminController

    def _get_handlers(self) -> list[BaseHandler | AdminHandler]:
        handlers = super()._get_handlers()
        handlers.extend(handler(self.dp, self.controller) for handler in handler_classes)
        return handlers
