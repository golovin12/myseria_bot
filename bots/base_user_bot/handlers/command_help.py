from aiogram.filters import Command
from aiogram.types import Message

from .user_base_handler import UserHandler
from ..consts import ControlCommand


class CommandHelp(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.HELP))(self.command_help)

    async def command_help(self, message: Message):
        """Помощь по боту"""
        await message.reply(f"Список доступных команд:\n{ControlCommand.all_commands}")
