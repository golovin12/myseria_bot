import asyncio
from dataclasses import dataclass
from datetime import datetime
from itertools import islice
from math import ceil
from typing import Iterable, AsyncIterable, AsyncIterator, Iterator

from aiogram import types
from fake_useragent import UserAgent

from consts import MONTH_NAMES_RU


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


async def message_per_seconds_limiter(async_generator: AsyncIterable, limit_messages: int = 15,
                                      limit_seconds: int = 60) -> AsyncIterator:
    """
    Ограничивает частоту отправки сообщений. Ограничение limit_messages/limit_seconds (количество сообщений/n секунд)
    """
    start_time = datetime.now()
    count = 0
    async for seria_info in async_generator:
        seconds_after_start = (datetime.now() - start_time).seconds
        if seconds_after_start <= limit_seconds:
            if count > limit_messages:
                await asyncio.sleep(limit_seconds - seconds_after_start)
        else:
            start_time = datetime.now()
            count = 0
        yield seria_info
        count += 1


def get_date_by_localize_date_string(date_string: str) -> datetime:
    """Формирует дату из строки вида: 29 сентября 2019"""
    day, month, year = date_string.split()
    month = MONTH_NAMES_RU[month]
    return datetime(day=int(day), month=month, year=int(year))


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


@dataclass
class Seria:
    name: str
    url: str
    release_date: str
    voices: list[str]


@dataclass
class Serial:
    name: str
    url: str
    last_season: str
    last_seria: Seria


class FindSerialsHelper:
    def __init__(self, serials: dict):
        self._all_serials = serials
        self.serials = set()
        self.search_dates = dict()
        self._fill_data()

    def _fill_data(self):
        for serial_name, last_date in self._all_serials.items():
            self.serials.add(serial_name)
            self.search_dates.setdefault(datetime.strptime(last_date, "%d.%m.%Y"), set()).add(serial_name)

    def get_date_and_update_serials(self) -> Iterator:
        """При запросе новой даты обновляет список сериалов"""
        for last_date, serials in sorted(self.search_dates.items()):
            yield last_date
            self.serials -= serials  # Удаляем сериалы, которые были привязаны к данной дате


class ExternalService:
    user_agent: UserAgent

    @staticmethod
    async def get_site_addr() -> str:
        """Получить адрес сайта"""
        ...

    async def exist(self, serial_name: str) -> bool:
        """Проверяет, есть ли сериал с таким названием"""
        ...

    async def get_new_series_from_date(self, find_serials_helper: FindSerialsHelper) -> AsyncIterator[Seria]:
        """Получить список новых серий у сериала с выбранной конкретной даты"""
        yield ...

    async def get_serial_info(self, serial_name: str) -> [Serial | None]:
        """Получить информацию о сериале"""
        ...
