import asyncio
import warnings
from unittest import TestCase

from config import settings


class DBTestCase(TestCase):
    """Класс для тестов, в которых используется подключение к бд.Очищает бд после каждого теста."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if settings.ENV_NAME != "TEST":
            raise Exception("Тесты, в которых есть работа с бд, "
                            "можно запускать только с переменной окружения ENV_NAME=TEST")

    def setUp(self) -> None:
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self) -> None:
        if settings.ENV_NAME == "TEST":
            # очищаем бд после работы
            asyncio.run(settings.aioredis.flushdb())
        warnings.simplefilter("default", ResourceWarning)
