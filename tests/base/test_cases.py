import asyncio
import warnings
from unittest import TestCase
from unittest.mock import patch, PropertyMock

from config import settings
from .redis_mock import AioredisMock


class ENVTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if settings.ENV_NAME != "TEST":
            raise Exception("Тесты можно запускать только с переменной окружения ENV_NAME=TEST")


class DBTestCase(ENVTestCase):
    """
    Класс для тестов, в которых используется подключение к бд.

    Очищает бд после каждого теста.
    """

    def setUp(self) -> None:
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self) -> None:
        if settings.ENV_NAME == "TEST":
            # очищаем бд после работы
            asyncio.run(settings.aioredis.flushdb())
        warnings.simplefilter("default", ResourceWarning)


class DBMockTestCase(ENVTestCase):
    """Класс для тестов, в которых используется redis_mock вместо подключения к бд"""
    patcher = patch('config.settings_test.TestSettings.aioredis', new_callable=PropertyMock)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        aioredis_mock = cls.patcher.start()
        aioredis_mock.return_value = AioredisMock()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.patcher.stop()
        super().tearDownClass()

    def tearDown(self) -> None:
        # очищаем бд после работы
        asyncio.run(settings.aioredis.flushdb())
