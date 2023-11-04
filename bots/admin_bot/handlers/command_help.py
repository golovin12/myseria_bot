import re

from aiogram.types import Message

from .admin_base_handler import AdminHandler
from ..consts import ControlCommand


class CommandHelp(AdminHandler):
    def _filter(self, message: Message):
        return re.fullmatch(rf'^{ControlCommand.HELP}$', message.text)

    def register_first(self):
        self.dp.message(self._filter)(self.command_help)

    async def command_help(self, message: Message):
        """Помощь по боту"""
        await message.reply(f"Список доступных команд:\n{ControlCommand.all_commands}")
