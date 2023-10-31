import re

from aiogram.types import Message

from .admin_base_handler import AdminHandler
from ..consts import ControlCommand


class CommandCreateAdmin(AdminHandler):
    def _filter(self, message: Message):
        return re.fullmatch(rf'^{ControlCommand.CREATE_ADMIN}$', message.text)

    def register_first(self):
        self.dp.message(self._filter)(self.command_create_admin)

    async def command_create_admin(self, message: Message):
        """Добавление администратора"""
        admin_id = int(message.text.replace('#create_admin: ', ''))
        result = await self.controller(message.from_user.id).create_admin(admin_id)
        await message.reply(result)
