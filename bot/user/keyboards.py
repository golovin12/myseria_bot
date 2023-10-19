from math import ceil

from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.consts import ControlCommand, PAGINATION_SERIALS_PREFIX, CallbackButtonInfo
from bot.utils import batched


def get_main_keyboard() -> types.ReplyKeyboardMarkup:
    buttons = (types.KeyboardButton(text=f"/{command}") for command, name in ControlCommand.choices)
    buttons = batched(buttons, 2)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите команду"
    )
    return keyboard


async def get_paginated_serials_keyboard(serials: iter, state: FSMContext, method: str = None, page: int = 0,
                                         items_on_page: int = 10) -> types.InlineKeyboardMarkup:
    # todo упростить код
    if method:
        await state.update_data(method=method)
    else:
        data = await state.get_data()
        method = data['method']
    management_btn_text = CallbackButtonInfo.method_name[method]

    max_pages = ceil(len(serials) / items_on_page)
    page = max_pages if page > max_pages else page
    end_buttons = []
    end_buttons.append(
        types.InlineKeyboardButton(text=f'Страница {page}', callback_data=f'{PAGINATION_SERIALS_PREFIX}-{page - 1}')
    ) if page > 0 else None
    end_buttons.append(types.InlineKeyboardButton(text=management_btn_text, callback_data=method))
    end_buttons.append(
        types.InlineKeyboardButton(text=f'Страница {page + 2}', callback_data=f'#page-{page + 1}')
    ) if page + 1 < max_pages else None

    serials = list(serials)[page * items_on_page:(page + 1) * items_on_page]
    keyboard_buttons = [[types.InlineKeyboardButton(text=serial, callback_data=serial)] for serial in serials]
    keyboard_buttons.append(end_buttons)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard
