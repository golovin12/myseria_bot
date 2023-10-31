from aiogram.types import Message

from .admin_base_handler import AdminHandler
from ..consts import ControlCommand


class CommandShowAdmins(AdminHandler):
    def _filter(self, message: Message):
        return message.text.startswith(ControlCommand.SHOW_ADMINS)

    def register_first(self):
        self.dp.message(self._filter)(self.command_show_admins)

    async def command_show_admins(self, message: Message):
        """Команда для получения id админов"""
        result = await self.controller(message.from_user.id).get_all_admins()
        await message.reply(result)
