from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from .user_base_handler import UserHandler
from ..consts import ControlCommand, CallbackButtonInfo
from ..keyboards import get_paginated_serials_keyboard
from ..states import UserState


class CommandSerialInfo(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.SERIAL_INFO))(self.command_serial_info)

    def register_second(self):
        self.dp.callback_query(StateFilter(UserState.serial_info))(self.get_serial_info)

    async def command_serial_info(self, message: Message, state: FSMContext):
        serials = await self.controller(message.from_user.id).get_user_serials()
        if not serials:
            await message.reply("Вы ещё не добавили сериалы для отслеживания. Чтобы добавить, нажмите: /add_serials")
            return
        await state.set_state(UserState.serial_info)
        keyboard = await get_paginated_serials_keyboard(serials, state, CallbackButtonInfo.CLOSE)
        await message.reply(
            "Ниже представлен список выбранных тобой сериалов, выбери о каком из них хочешь получить информацию.",
            reply_markup=keyboard)

    async def get_serial_info(self, callback_query: CallbackQuery, state: FSMContext):
        """Получение актуальной информации о сериале"""
        await callback_query.answer('Подождите, информация собирается...')
        if callback_query.data == CallbackButtonInfo.CLOSE:
            await state.clear()
            await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
            return
        serial_name = str(callback_query.data)
        info = await self.controller(callback_query.from_user.id).get_serial_info(serial_name)
        await callback_query.message.answer(info, disable_web_page_preview=True)
