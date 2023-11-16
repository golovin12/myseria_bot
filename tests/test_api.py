from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import bot_router
from config import settings
from .base import DBMockTestCase


class BotApiTest(DBMockTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.routes = bot_router.routes
        app = FastAPI()
        app.include_router(bot_router)
        self.client = TestClient(app)
        self.invalid_headers = {'X-Telegram-Bot-Api-Secret-Token': 'invalid'}
        self.valid_headers = {'X-Telegram-Bot-Api-Secret-Token': settings.SECRET_TOKEN}

        # mock ботов
        bot_mock = AsyncMock()
        bot_mock.process_new_updates.return_value = None

        self.bots_patcher = patch('config.settings_test.TestSettings.user_bots')
        user_bots_mock = self.bots_patcher.start()
        user_bots_mock.__getitem__.return_value = bot_mock

    def test_verify_token(self):
        """
        Проверки:
         1) все точки входа валидируют токен.
         2) проверка статусов ответов
         """
        for route in self.routes:
            # Заголовок с токеном отсутствует
            response = self.client.post(route.path)
            self.assertEqual(response.status_code, 422)
            # Заголовок с токеном не валиден
            response = self.client.post(route.path, headers=self.invalid_headers)
            self.assertEqual(response.status_code, 422)
            # Заголовок с токеном валиден
            response = self.client.post(route.path, json={}, headers=self.valid_headers)
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:
        self.bots_patcher.stop()
        super().tearDown()

