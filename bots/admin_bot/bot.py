from .controller import AdminController
from .handlers import handler_classes, AdminHandler
from bots.base_bot import BaseBot
from .middlewares import AdminOnlyMiddleware


class AdminBot(BaseBot):
    controller = AdminController

    def _get_handlers(self) -> list[AdminHandler]:
        return [handler(self.dp, self.controller) for handler in handler_classes]

    def _register_middlewares(self):
        self.dp.update.outer_middleware(AdminOnlyMiddleware(self.bot))
        super()._register_middlewares()
