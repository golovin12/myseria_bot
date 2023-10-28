import re

from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from .consts import PAGINATION_SERIALS_PREFIX
from .controller import UserController
from .keyboards import get_paginated_serials_keyboard

router = Router()


@router.callback_query(lambda callback_query: re.fullmatch(fr'^{PAGINATION_SERIALS_PREFIX}-\d+$', callback_query.data))
async def paginate_serials(callback_query: types.CallbackQuery, state: FSMContext):
    # Обновление клавиатуры при пагинации
    await callback_query.answer()
    page = int(callback_query.data.replace(f"{PAGINATION_SERIALS_PREFIX}-", ""))
    serials = await UserController(callback_query.from_user.id).get_user_serials()
    keyboard = await get_paginated_serials_keyboard(serials, state, page=page)
    await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=keyboard)
