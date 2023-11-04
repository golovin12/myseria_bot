from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .user_base_handler import UserHandler
from ..consts import ControlCommand
from ..states import UserState


class CommandAddSerial(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.ADD_SERIAL))(self.command_add_serial)

    def register_second(self):
        self.dp.message(StateFilter(UserState.add_serial))(self.add_serial)

    async def command_add_serial(self, message: Message, state: FSMContext):
        await state.set_state(UserState.add_serial)
        await message.reply("Отправляйте боту названия сериалов, которые хотите добавить (по одному):")

    async def add_serial(self, message: Message):
        """Добавление сериала в список отслеживания"""
        serial_name = str(message.text)
        await message.reply("Подождите, сериал проверяется...")
        user_controller = self.controller(message.from_user.id)
        is_added = await user_controller.add_serial(serial_name)
        if is_added:
            await message.answer(
                f"Сериал {serial_name} был успешно добавлен!\nМожете указать название другого сериала для добавления."
            )
        else:
            host = await user_controller.serial_service.get_host()
            await message.answer(
                f"Не удалось добавить сериал {serial_name} "
                f"(убедитесь, что сериал с таким названием есть на сайте {host})",
                disable_web_page_preview=True
            )
