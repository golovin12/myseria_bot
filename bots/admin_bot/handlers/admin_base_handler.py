from typing import Type

from aiogram import Dispatcher

from bots.base_bot import BaseHandler
from ..controller import AdminController


class AdminHandler(BaseHandler):
    """Шаблонный хандлер админа."""

    def __init__(self, dp: Dispatcher, controller: Type[AdminController]):
        super().__init__(dp)
        self.controller = controller
