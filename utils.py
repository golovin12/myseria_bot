from itertools import islice
from math import ceil
from typing import Iterable

from aiogram import types


def batched(iterable: Iterable, n: int):
    """
    >>> batched([1, 2, 3, 4, 5], 2)
    [1, 2] [3, 4] [5]
    """
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


class ButtonPaginator:
    def __init__(self, main_btn_text: str, main_btn_callback: str, page_prefix: str = '', items_on_page: int = 10):
        self.items_on_page = items_on_page
        self.page_prefix = page_prefix
        self.main_btn_callback = main_btn_callback
        self.main_btn_text = main_btn_text

    def get_paginated_keyboard(self, serials: iter, query_string: str = "") -> types.InlineKeyboardMarkup:
        page = 0
        if query_string:
            page = query_string.replace(self.page_prefix, '')
            page = int(page) if page.isdigit() else 0
        return self._get_serials_page_keyboard(serials, page=page)

    def _get_serials_page_keyboard(self, serials: iter, page: int) -> types.InlineKeyboardMarkup:
        max_pages = ceil(len(serials) / self.items_on_page)
        page = max_pages if page > max_pages else page
        end_buttons = []
        end_buttons.append(
            types.InlineKeyboardButton(text=f'Страница {page}', callback_data=f'#page-{page - 1}')
        ) if page > 0 else None
        end_buttons.append(types.InlineKeyboardButton(text=self.main_btn_text, callback_data=self.main_btn_callback))
        end_buttons.append(
            types.InlineKeyboardButton(text=f'Страница {page + 2}', callback_data=f'#page-{page + 1}')
        ) if page + 1 < max_pages else None

        serials = list(serials)[page * self.items_on_page:(page + 1) * self.items_on_page]
        keyboard_buttons = [[types.InlineKeyboardButton(text=serial, callback_data=serial)] for serial in serials]
        keyboard_buttons.append(end_buttons)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        return keyboard
