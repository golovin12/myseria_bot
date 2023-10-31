from aiogram.filters import Command
from aiogram.types import Message

from .user_base_handler import UserHandler
from ..consts import ControlCommand


class CommandReboot(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.REBOOT))(self.command_reboot)

    async def command_reboot(self, message: Message):
        """Сбрасывает список отслеживаемых сериалов"""
        is_reboot = await self.controller(message.from_user.id).reboot()
        if is_reboot:
            await message.reply("Информация о Вас успешно сброшена.")
        else:
            await message.reply("Сброс не удался, повторите попытку")
