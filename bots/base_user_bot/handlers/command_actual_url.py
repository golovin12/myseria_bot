from aiogram.filters import Command
from aiogram.types import Message

from .user_base_handler import UserHandler
from ..consts import ControlCommand


class CommandActualUrl(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.ACTUAL_URL))(self.command_actual_url)

    async def command_actual_url(self, message: Message):
        """Приветствие"""
        await message.reply(await self.controller(message.from_user.id).get_actual_url())
