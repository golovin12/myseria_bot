import abc

from aiogram import Dispatcher


class BaseHandler(abc.ABC):
    """Шаблонный хандлер."""
    def __init__(self, dp: Dispatcher):
        self.dp = dp

    def register_first(self):
        """Регистрация хандлеров, которые должны выполняться всегда (в основном - обработчики команд)"""
        # dp.message(filter)(method)
        ...

    def register_second(self):
        """Регистрация хандлеров, которые зависят от состояний"""
        # dp.callback_query(filter)(method)
        ...
