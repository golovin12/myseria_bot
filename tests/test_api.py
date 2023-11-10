import asyncio
import warnings
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import bot_router
from config import settings
from consts import ADMIN_KEY, MySeria, Zetflix
from database.models import Admin
from .base_test_case import DBTestCase


class BotApiTest(DBTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.routes = bot_router.routes
        app = FastAPI()
        app.include_router(bot_router)
        self.client = TestClient(app)
        self.invalid_headers = {'X-Telegram-Bot-Api-Secret-Token': 'invalid'}
        self.valid_headers = {'X-Telegram-Bot-Api-Secret-Token': settings.SECRET_TOKEN}

        self.bot_mock = AsyncMock()
        self.bot_mock.process_new_updates.return_value = None
        settings.user_bots[MySeria.KEY] = self.bot_mock
        settings.user_bots[Zetflix.KEY] = self.bot_mock
        settings.user_bots[ADMIN_KEY] = self.bot_mock

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

    def test_admin_router(self):
        """Проверка доступа (только для админов)"""
        self.bot_mock.process_new_updates.call_count = 0
        # пустой запрос
        self.client.post(f'/bot/{ADMIN_KEY}', json={}, headers=self.valid_headers)
        self.assertEqual(self.bot_mock.process_new_updates.call_count, 0)
        # не валидный id юзера
        self.client.post(f'/bot/{ADMIN_KEY}', json={'message': {'from': {'id': None}}}, headers=self.valid_headers)
        self.assertEqual(self.bot_mock.process_new_updates.call_count, 0)
        # запрос не от админа
        self.client.post(f'/bot/{ADMIN_KEY}', json={'message': {'from': {'id': settings.ADMIN_ID}}},
                         headers=self.valid_headers)
        self.assertEqual(self.bot_mock.process_new_updates.call_count, 0)
        # запрос от админа
        self._create_admin()
        self.client.post(f'/bot/{ADMIN_KEY}', json={'message': {'from': {'id': settings.ADMIN_ID}}},
                         headers=self.valid_headers)
        self.assertEqual(self.bot_mock.process_new_updates.call_count, 1)

    def _create_admin(self):
        warnings.simplefilter("ignore", ResourceWarning)
        asyncio.run(Admin(settings.ADMIN_ID, is_admin=True).save())
