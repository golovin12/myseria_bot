import re

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .user_base_handler import UserHandler
from ..keyboards import get_paginated_serials_keyboard
from ..consts import PAGINATION_SERIALS_PREFIX


class Paginator(UserHandler):

    @staticmethod
    def _filter_pagination(callback_query: CallbackQuery):
        return re.fullmatch(fr'^{PAGINATION_SERIALS_PREFIX}-\d+$', callback_query.data)

    def register_first(self):
        self.dp.callback_query(self._filter_pagination)(self.paginate_serials)

    async def paginate_serials(self, callback_query: CallbackQuery, state: FSMContext):
        """Обновление клавиатуры при пагинации"""
        await callback_query.answer()
        page = int(callback_query.data.replace(f"{PAGINATION_SERIALS_PREFIX}-", ""))
        serials = await self.controller(callback_query.from_user.id).get_user_serials()
        keyboard = await get_paginated_serials_keyboard(serials, state, page=page)
        await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=keyboard)
