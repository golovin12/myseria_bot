import re

from aiogram.types import Message

from .admin_base_handler import AdminHandler
from ..consts import ControlCommand


class CommandDeleteAdmin(AdminHandler):
    def _filter(self, message: Message):
        return re.fullmatch(rf'^{ControlCommand.DELETE_ADMIN}$', message.text)

    def register_first(self):
        self.dp.message(self._filter)(self.command_delete_admin)

    async def command_delete_admin(self, message: Message):
        """Удаление администратора"""
        admin_id = int(message.text.replace('#delete_admin: ', ''))
        result = await self.controller(message.from_user.id).delete_admin(admin_id)
        await message.reply(result)
