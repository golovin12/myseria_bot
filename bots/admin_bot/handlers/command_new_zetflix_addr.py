import re

from aiogram.types import Message

from .admin_base_handler import AdminHandler
from ..consts import ControlCommand


class CommandNewZetflixAddr(AdminHandler):
    def _filter(self, message: Message):
        return re.fullmatch(rf'^{ControlCommand.NEW_ZETFLIX_ADDR}$', message.text)

    def register_first(self):
        self.dp.message(self._filter)(self.command_new_zetflix_addr)

    async def command_new_zetflix_addr(self, message: Message):
        """Команда для обновления адреса сайта вручную"""
        url = message.text.replace('#new_zetflix_addr: ', '').removesuffix('/')
        result = await self.controller(message.from_user.id).force_update_zetflix_url(url)
        await message.reply(result)
