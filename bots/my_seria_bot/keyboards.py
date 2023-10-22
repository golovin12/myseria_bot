import itertools
from math import ceil

from aiogram import types
from aiogram.fsm.context import FSMContext

from utils import batched
from .consts import ControlCommand, PAGINATION_SERIALS_PREFIX, CallbackButtonInfo


def get_main_keyboard() -> types.ReplyKeyboardMarkup:
    buttons = (types.KeyboardButton(text=f"/{command}") for command, desc in ControlCommand.choices)
    buttons = batched(buttons, 2)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,  # noqa
        resize_keyboard=True,
        input_field_placeholder="Выберите команду"
    )
    return keyboard


def get_menu_commands() -> list[types.BotCommand]:
    bot_commands = [
        types.BotCommand(command=f'/{command}', description=desc) for command, desc in ControlCommand.choices
    ]
    return bot_commands


async def get_paginated_serials_keyboard(serials: dict[str, str], state: FSMContext, method: str = "", page: int = 0,
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

    page_serials = itertools.islice(serials.keys(), page * items_on_page, (page + 1) * items_on_page)
    keyboard_buttons = [[types.InlineKeyboardButton(text=serial, callback_data=serial)] for serial in page_serials]
    keyboard_buttons.append(end_buttons)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard
