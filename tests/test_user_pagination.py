import asyncio
from unittest.mock import AsyncMock

from bots.base_user_bot.consts import CallbackButtonInfo
from bots.base_user_bot.keyboards import get_paginated_serials_keyboard
from .base import TestCase


class StateMock(AsyncMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = {}

    async def update_data(self, **kwargs):
        self._data |= kwargs

    async def get_data(self):
        return self._data


class PaginatorTest(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.state_mock = StateMock()

    def test_keyboard_pagination(self):
        # передаём пустой список
        method = CallbackButtonInfo.ALL
        keyboard = asyncio.run(get_paginated_serials_keyboard([], self.state_mock, method=method))
        self.assertEqual(len(keyboard.inline_keyboard), 1)

        serials = [f'serial{i}' for i in range(11)]
        # первая страница списка из 11 сериалов
        keyboard = asyncio.run(get_paginated_serials_keyboard(serials, self.state_mock, method=method))
        self.assertEqual(len(keyboard.inline_keyboard), 11)
        # вторая страница списка из 11 сериалов
        keyboard = asyncio.run(get_paginated_serials_keyboard(serials, self.state_mock, method=method, page=1))
        self.assertEqual(len(keyboard.inline_keyboard), 2)
        # последняя страница списка из 11 сериалов
        keyboard = asyncio.run(get_paginated_serials_keyboard(serials, self.state_mock, method=method, page=999))
        self.assertEqual(len(keyboard.inline_keyboard), 2)
        # страница со всеми сериалами
        keyboard = asyncio.run(get_paginated_serials_keyboard(serials, self.state_mock, method=method, page=999,
                                                              page_size=20))
        self.assertEqual(len(keyboard.inline_keyboard), 12)

    def test_keyboard_end_buttons(self):
        method = CallbackButtonInfo.ALL
        keyboard = asyncio.run(get_paginated_serials_keyboard([], self.state_mock, method=method))
        self.assertEqual(self.state_mock._data['method'], method)
        end_buttons = keyboard.inline_keyboard[-1]
        self.assertEqual(len(end_buttons), 1)
        self.assertEqual(end_buttons[0].callback_data, method)

        serials = [f'serial{i}' for i in range(11)]
        # первая страница списка из 11 сериалов
        keyboard = asyncio.run(get_paginated_serials_keyboard(serials, self.state_mock, page_size=3))
        end_buttons = keyboard.inline_keyboard[-1]
        self.assertEqual(len(end_buttons), 2)
        self.assertEqual(end_buttons[0].callback_data, method)
        # вторая страница списка из 11 сериалов
        method = CallbackButtonInfo.CLOSE
        keyboard = asyncio.run(get_paginated_serials_keyboard(serials, self.state_mock, method=method, page=1,
                                                              page_size=3))
        self.assertEqual(self.state_mock._data['method'], method)
        end_buttons = keyboard.inline_keyboard[-1]
        self.assertEqual(len(end_buttons), 3)
        self.assertEqual(end_buttons[1].callback_data, method)
        # последняя страница списка из 11 сериалов
        keyboard = asyncio.run(get_paginated_serials_keyboard(serials, self.state_mock, page=999, page_size=3))
        end_buttons = keyboard.inline_keyboard[-1]
        self.assertEqual(len(end_buttons), 2)
        self.assertEqual(end_buttons[1].callback_data, method)
        # страница со всеми сериалами
        keyboard = asyncio.run(get_paginated_serials_keyboard(serials, self.state_mock, page=999, page_size=20))
        end_buttons = keyboard.inline_keyboard[-1]
        self.assertEqual(len(end_buttons), 1)
        self.assertEqual(end_buttons[0].callback_data, method)
