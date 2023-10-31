from typing import Type

from aiogram import Dispatcher

from base_bot import BaseHandler
from ..controller import UserController


class UserHandler(BaseHandler):
    """Шаблонный хандлер юзера."""

    def __init__(self, dp: Dispatcher, controller: Type[UserController]):
        super().__init__(dp)
        self.controller = controller
