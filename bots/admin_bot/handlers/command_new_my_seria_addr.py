import re

from aiogram.types import Message

from .admin_base_handler import AdminHandler
from ..consts import ControlCommand


class CommandNewMySeriaAddr(AdminHandler):
    def _filter(self, message: Message):
        return re.fullmatch(rf'^{ControlCommand.NEW_MY_SERIA_ADDR}$', message.text)

    def register_first(self):
        self.dp.message(self._filter)(self.command_new_my_seria_addr)

    async def command_new_my_seria_addr(self, message: Message):
        """Команда для обновления адреса сайта вручную"""
        url = message.text.replace('#new_my_seria_addr: ', '').removesuffix('/')
        result = await self.controller(message.from_user.id).force_update_my_seria_url(url)
        await message.reply(result)
