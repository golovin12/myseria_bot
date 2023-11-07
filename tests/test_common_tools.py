import asyncio
import json
from collections import UserDict
from datetime import datetime
from typing import AsyncIterator, AsyncIterable
from unittest import TestCase
from unittest.mock import patch

from common_tools.async_connection import url_is_active
from common_tools.async_sequence import message_per_seconds_limiter
from common_tools.date import get_date_by_localize_date_string
from common_tools.json_serializer import dict_date_serializer
from common_tools.sequence import batched


class CommonToolsTest(TestCase):
    def test_url_is_active(self):
        with patch('aiohttp.request') as mock_request:
            client_response = mock_request.return_value.__aenter__.return_value
            # адрес активен
            client_response.status = 200
            self.assertEqual(asyncio.run(url_is_active('http://test')), True)
            # адрес не активен
            client_response.status = 404
            self.assertEqual(asyncio.run(url_is_active('http://test')), False)

    def test_message_limiter(self):
        # Ограничение - 3 сообщения в 4 секунды
        limit_messages = 3
        limit_seconds = 4

        async def async_range(count: int) -> AsyncIterator[int]:
            """Имитация итератора сообщений"""
            for i in range(count):
                yield i

        async def collect(ait: AsyncIterable) -> list:
            """Сборка сообщений в список"""
            return [i async for i in ait]

        # test_case = (количество отправляемых сообщений, максимально ожидаемое время отправки сообщений)
        test_case1 = (limit_messages * 0, limit_seconds * 0)  # Количество отправляемых сообщений == 0
        test_case2 = (limit_messages * 1, limit_seconds * 0)  # Количество отправляемых сообщений <= limit_messages
        test_case3 = (limit_messages * 1 + 1, limit_seconds * 1)  # Количество отправляемых сообщений > limit_messages
        for messages_count, max_sending_time in (test_case1, test_case2, test_case3):
            async_iterator = async_range(messages_count)
            messages_iterator = message_per_seconds_limiter(async_iterator,
                                                            limit_messages=limit_messages,
                                                            limit_seconds=limit_seconds)
            time_start = datetime.now()
            result = asyncio.run(collect(messages_iterator))
            self.assertLessEqual((datetime.now() - time_start).seconds, max_sending_time)
            self.assertEqual(result, list(range(messages_count)))

    def test_localize_date(self):
        self.assertEqual(get_date_by_localize_date_string('24 октября 2019'), datetime(day=24, month=10, year=2019))

    def test_dict_date_serializer(self):
        test_dict = UserDict({'test_date': datetime(day=24, month=10, year=2019)})
        result = json.dumps(test_dict, default=dict_date_serializer)
        self.assertEqual(result, '{"test_date": "24.10.2019"}')

    def test_batched(self):
        self.assertEqual(tuple(batched('AABBCC', 2)), (('A', 'A'), ('B', 'B'), ('C', 'C')))
        self.assertEqual(tuple(batched([1, 2, 3], 2)), ((1, 2), (3,)))
        self.assertEqual(tuple(batched([1, 2, 3], 3)), ((1, 2, 3),))
        self.assertEqual(tuple(batched([1, 2, 3], 1)), ((1,), (2,), (3,),))
        raise_batch = batched([1, 2, 3], 0)
        self.assertRaises(ValueError, tuple, raise_batch)
