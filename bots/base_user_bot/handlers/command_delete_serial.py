from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from .user_base_handler import UserHandler
from ..consts import ControlCommand, CallbackButtonInfo
from ..keyboards import get_paginated_serials_keyboard
from ..states import UserState


class CommandDeleteSerial(UserHandler):
    def register_first(self):
        self.dp.message(Command(ControlCommand.DELETE_SERIAL))(self.command_delete_serial)

    def register_second(self):
        self.dp.callback_query(StateFilter(UserState.delete_serial))(self.delete_serial)

    async def command_delete_serial(self, message: Message, state: FSMContext):
        await state.set_state(UserState.delete_serial)
        serials = await self.controller(message.from_user.id).get_user_serials()
        keyboard = await get_paginated_serials_keyboard(serials, state, CallbackButtonInfo.CLOSE)
        await message.reply("Выберите сериал, который хотите удалить", reply_markup=keyboard)

    async def delete_serial(self, callback_query: CallbackQuery, state: FSMContext):
        """Удаление сериала из списка отслеживания"""
        await callback_query.answer()
        if callback_query.data == CallbackButtonInfo.CLOSE:
            await state.clear()
            await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
            return
        serial_name = str(callback_query.data)
        user_controller = self.controller(callback_query.from_user.id)
        is_deleted = await user_controller.delete_serial(serial_name)
        if is_deleted:
            serials = await user_controller.get_user_serials()
            keyboard = await get_paginated_serials_keyboard(serials, state, CallbackButtonInfo.CLOSE)
            await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=keyboard)
            await callback_query.message.answer(
                f"Сериал {serial_name} был успешно удален!\nМожете выбрать ещё сериал для удаления."
            )
        else:
            await callback_query.message.answer(
                f"Не удалось удалить сериал {serial_name}, возможно он отсутствует в списке отслеживаемых сериалов"
            )
