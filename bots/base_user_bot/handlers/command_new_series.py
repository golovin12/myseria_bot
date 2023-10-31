from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from common_tools.async_sequence import message_per_seconds_limiter
from .user_base_handler import UserHandler
from ..consts import ControlCommand, CallbackButtonInfo
from ..keyboards import get_paginated_serials_keyboard
from ..states import UserState


class CommandNewSeries(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.NEW_SERIES))(self.command_new_series)

    def register_second(self):
        self.dp.callback_query(StateFilter(UserState.new_series))(self.get_new_series)

    async def command_new_series(self, message: Message, state: FSMContext):
        """Получить информацию о новых сериях"""
        await state.set_state(UserState.new_series)
        serials = await self.controller(message.from_user.id).get_user_serials()
        keyboard = await get_paginated_serials_keyboard(serials, state, CallbackButtonInfo.ALL)
        await message.reply("Выберите сериал, по которому хотите получить новинки", reply_markup=keyboard)

    async def get_new_series(self, callback_query: CallbackQuery, state: FSMContext):
        """Получение информации о новых сериях"""
        await state.clear()
        await callback_query.answer()
        await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
        await callback_query.message.answer("Подождите, информация собирается...")
        serial_name = str(callback_query.data)
        if serial_name == CallbackButtonInfo.ALL:
            new_series = self.controller(callback_query.from_user.id).get_new_series()
        else:
            new_series = self.controller(callback_query.from_user.id).get_new_series(serial_name)
        async for seria_info in message_per_seconds_limiter(new_series):
            await callback_query.message.answer(seria_info, disable_web_page_preview=True)
