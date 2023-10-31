from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .user_base_handler import UserHandler
from ..consts import ControlCommand


class CommandCancel(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.CANCEL))(self.command_cancel)
        self.dp.message(F.text.lower() == 'отмена')(self.command_cancel)

    async def command_cancel(self, message: Message, state: FSMContext):
        """Отмена операции и сброс любого состояния"""
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()
        await message.reply('Операция отменена')
