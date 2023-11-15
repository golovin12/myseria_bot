import itertools
from math import ceil

from aiogram import types
from aiogram.fsm.context import FSMContext

from common_tools.sequence import batched
from .consts import ControlCommand, PAGINATION_SERIALS_PREFIX, CallbackButtonInfo


def get_main_keyboard() -> types.ReplyKeyboardMarkup:
    """Получить клавиатуру с командами бота"""
    buttons = (types.KeyboardButton(text=f"/{command}") for command, desc in ControlCommand.choices)
    buttons = batched(buttons, 2)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,  # type: ignore
        resize_keyboard=True,
        input_field_placeholder="Выберите команду"
    )
    return keyboard


def get_menu_commands() -> list[types.BotCommand]:
    """Получить список команд бота"""
    bot_commands = [
        types.BotCommand(command=f'/{command}', description=desc) for command, desc in ControlCommand.choices
    ]
    return bot_commands


async def get_paginated_serials_keyboard(serials: list[str], state: FSMContext, method: str = "", page: int = 0,
                                         page_size: int = 10) -> types.InlineKeyboardMarkup:
    # Получение информации о текущем состоянии пагинации
    if method:
        await state.update_data(method=method)
    else:
        data = await state.get_data()
        method = data['method']
    # Пагинация сериалов
    last_page = (ceil(len(serials) / page_size) or 1) - 1
    page = last_page if page > last_page else page
    page_serials = itertools.islice(serials, page * page_size, (page + 1) * page_size)
    keyboard_buttons = [[types.InlineKeyboardButton(text=serial, callback_data=serial)] for serial in page_serials]
    # Добавление кнопок пагинации (предыдущая стр. и следующая стр.) + кнопка управления (для выхода из клавиатуры)
    end_buttons = []
    end_buttons.append(
        types.InlineKeyboardButton(text=f'Страница {page}', callback_data=f'{PAGINATION_SERIALS_PREFIX}-{page - 1}')
    ) if page > 0 else None
    end_buttons.append(types.InlineKeyboardButton(text=CallbackButtonInfo.method_name[method], callback_data=method))
    end_buttons.append(
        types.InlineKeyboardButton(text=f'Страница {page + 2}', callback_data=f'#page-{page + 1}')
    ) if page + 1 < last_page else None

    keyboard_buttons.append(end_buttons)
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
