from aiogram.filters import Command
from aiogram.types import Message

from .user_base_handler import UserHandler
from ..keyboards import get_main_keyboard
from ..consts import ControlCommand


class CommandStart(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.START))(self.command_start)

    async def command_start(self, message: Message):
        """Приветствие"""
        await message.reply(
            "Привет, данный бот предназначен для отслеживания выхода серий с сайта MySeria.\n"
            "Вы можете создать свой список для отслеживания сериалов и получать актуальную информацию о новых сериях.\n"
            "Также данный бот может показать вышедшие озвучки для конкретной серии.\n"
            f"Список команд, для работы с ботом представлен ниже:\n{ControlCommand.all_commands}",
            reply_markup=get_main_keyboard())
