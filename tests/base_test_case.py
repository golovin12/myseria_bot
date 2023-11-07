import asyncio
import warnings
from unittest import TestCase

from config import settings


class DBTestCase(TestCase):
    def setUp(self) -> None:
        if settings.ENV_NAME != "TEST":
            raise Exception("Тесты можно запускать только с переменной окружения ENV_NAME=TEST")

    def tearDown(self) -> None:
        warnings.simplefilter("ignore", ResourceWarning)
        if settings.ENV_NAME == "TEST":
            # очищаем бд после работы
            asyncio.run(settings.aioredis.flushdb())
