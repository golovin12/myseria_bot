import asyncio
from datetime import date, timedelta
from typing import AsyncIterable
from unittest.mock import AsyncMock, Mock

from bots.base_user_bot.controller import UserController
from database.models import User
from serial_services import UserSerials, Serial, Seria
from .base import DBMockTestCase

serial_service_mock = AsyncMock()


class SiteUserController(UserController):
    serial_service_class = Mock(return_value=serial_service_mock)


class UserControllerTest(DBMockTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user_id = 2
        self.serials = UserSerials({'serial1': date.today(),
                                    'serial2': date.today(),
                                    'serial3': date.today() - timedelta(days=3)})
        asyncio.run(User(self.user_id, self.serials).save())

    def test_add_serial(self):
        # Добавление сериала несуществующему юзеру
        serial_service_mock.exist.return_value = True
        self.assertTrue(asyncio.run(SiteUserController(999).add_serial('serial4')))
        new_user = asyncio.run(User.get_object(999))
        self.assertEqual(len(new_user.serials), 1)
        # Добавление сериала юзеру cо списком сериалов
        serial_service_mock.exist.return_value = True
        self.assertTrue(asyncio.run(SiteUserController(self.user_id).add_serial('serial4')))
        user = asyncio.run(User.get_object(self.user_id))
        self.assertEqual(len(user.serials), len(self.serials) + 1)
        self.assertEqual(serial_service_mock.exist.call_count, 2)
        # Попытка повторного добавления сериала (возможно в другом регистре)
        self.assertTrue(asyncio.run(SiteUserController(self.user_id).add_serial('SERIAL4')))
        self.assertEqual(serial_service_mock.exist.call_count, 2)
        # Попытка добавления сериала, которого нет на сайте
        serial_service_mock.exist.return_value = False
        self.assertFalse(asyncio.run(SiteUserController(self.user_id).add_serial('serial5')))
        user = asyncio.run(User.get_object(self.user_id))
        self.assertEqual(len(user.serials), len(self.serials) + 1)

    def test_delete_serial(self):
        # Попытка удаления сериала, у несуществующего юзера
        self.assertFalse(asyncio.run(SiteUserController(999).delete_serial('serial1')))
        # Попытка удаления сериала, которого нет у юзера
        self.assertFalse(asyncio.run(SiteUserController(self.user_id).delete_serial('serial4')))
        # Удаление сериала, который был у юзера
        self.assertTrue(asyncio.run(SiteUserController(self.user_id).delete_serial('SERIAL1')))
        user = asyncio.run(User.get_object(self.user_id))
        self.assertEqual(len(user.serials), len(self.serials) - 1)

    def test_reboot(self):
        # Очистка сериалов у несуществующего юзера
        self.assertTrue(asyncio.run(SiteUserController(999).reboot()))
        # Очистка сериалов у существующего юзера
        user = asyncio.run(User.get_object(self.user_id))
        self.assertEqual(len(user.serials), len(self.serials))
        self.assertTrue(asyncio.run(SiteUserController(self.user_id).reboot()))
        user = asyncio.run(User.get_object(self.user_id))
        self.assertEqual(len(user.serials), 0)

    def test_get_user_serials(self):
        # получение списка сериалов у несуществующего юзера
        user_serials = asyncio.run(SiteUserController(999).get_user_serials())
        self.assertEqual(user_serials, [])
        # получение списка сериалов у существующего юзера
        user_serials = asyncio.run(SiteUserController(self.user_id).get_user_serials())
        self.assertEqual(user_serials, ['Serial1', 'Serial2', 'Serial3'])

    def test_get_serial_info(self):
        # попытка получения информации о неизвестном сериале
        serial_service_mock.get_serial_info.return_value = None
        serial_info = asyncio.run(SiteUserController(self.user_id).get_serial_info('serial4'))
        self.assertEqual(serial_info.count('\n'), 0)
        # получение информации о сериале
        serial = Serial('seria1', '', '', Seria('', '', '', []))
        serial_service_mock.get_serial_info.return_value = serial
        serial_info = asyncio.run(SiteUserController(self.user_id).get_serial_info('serial1'))
        self.assertLess(0, serial_info.count('\n'))

    def test_get_new_series(self):
        async def get_series(serials):
            for serial_name in serials:
                yield Seria(serial_name, '', '', [])
                yield Seria(serial_name, '', '', [])

        async def collect(ait: AsyncIterable) -> list:
            """Сборка сообщений в список"""
            return [i async for i in ait]

        serial_service_mock.get_new_series = get_series
        # получение информации о новых сериях когда сериалов у юзера нет / о сериале, который юзер не отслеживает
        for user_id, serial_filter in ((999, None), (999, 'serial1'), (self.user_id, 'serial4')):
            result = asyncio.run(collect(SiteUserController(user_id).get_new_series(serial_filter)))
            self.assertEqual(len(result), 1)
        # получение информации о новых сериях юзера - для одного сериала
        result = asyncio.run(collect(SiteUserController(self.user_id).get_new_series('SERIAL1')))
        self.assertEqual(len(result), 2)
        # получение информации о всех новых сериях юзера
        result = asyncio.run(collect(SiteUserController(self.user_id).get_new_series()))
        self.assertEqual(len(result), len(self.serials) * 2)

    def test_get_actual_url(self):
        serial_service_mock.get_actual_url.return_value = "https://test_url.com"
        self.assertEqual(asyncio.run(SiteUserController(self.user_id).get_actual_url()), "https://test_url.com")
