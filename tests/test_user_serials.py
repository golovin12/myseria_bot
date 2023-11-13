from datetime import datetime, timedelta

from serial_services import UserSerials
from .base import TestCase


class UserSerialsTest(TestCase):
    def setUp(self) -> None:
        self.dt_now = datetime.now()
        self.date_now = self.dt_now.date()
        self.serials = UserSerials({'serial1': self.dt_now,
                                    'serial2': self.date_now,
                                    'serial3': '19.03.2000',
                                    'serial4': self.date_now - timedelta(days=10)})

    def test_contains(self):
        # проверка на вхождение ключа в разных регистрах
        self.assertTrue('serial1' in self.serials)
        self.assertTrue('Serial1' in self.serials)
        # проверка на вхождение неизвестного
        self.assertFalse('serial_unknown' in self.serials)
        self.assertFalse('' in self.serials)
        self.assertRaises(AttributeError, lambda x: x in self.serials, 1)
        self.assertRaises(AttributeError, lambda x: x in self.serials, None)

    def test_get_item(self):
        # Получение значения по ключу в разных регистрах
        self.assertEqual(self.serials['Serial1'], self.date_now)
        self.assertEqual(self.serials['serial1'], self.date_now)
        self.assertEqual(self.serials.get('SERIAL1'), self.date_now)
        # получение значения по неизвестному ключу
        self.assertIsNone(self.serials.get('serial_unknown'))

    def test_set_item(self):
        # попытка установить ключ не в строковом формате
        self.assertRaises(AttributeError, UserSerials, {123: self.date_now})
        # попытка установить значение ключа с невалидным значением
        for value in (None, 123, 'string', '33.1.1999'):
            self.assertRaises(ValueError, UserSerials, {'serial_name': value})
        # Установка значения в виде datetime или datetime.strftime('%d.%m.%Y')
        serials1 = UserSerials({'serial_name': self.dt_now})
        serials2 = UserSerials({'serial_name': self.date_now.strftime('%d.%m.%Y')})
        serials3 = UserSerials({'serial_name': self.date_now})
        self.assertTrue(serials1 == serials2 == serials3)

    def test_actualize(self):
        modify_serials = self.serials.copy()
        # передача в actualize пустого набора сериалов
        modify_serials.actualize(UserSerials())
        self.assertEqual(modify_serials, self.serials)
        # передача в actualize сериала, у которого дата последнего изменения - сегодня
        modify_serials.actualize(self.serials.filter('serial1'))
        self.assertEqual(modify_serials, self.serials)
        # передача в actualize сериала, у которого дата последнего изменения не сегодня
        modify_serials.actualize(self.serials.filter('serial3'))
        self.assertNotEqual(modify_serials, self.serials)
        self.assertEqual(modify_serials['serial3'], self.date_now)
        self.assertEqual(modify_serials['serial4'], self.date_now - timedelta(days=10))
        # передача в actualize всех сериалов
        modify_serials.actualize(self.serials)
        self.assertNotEqual(modify_serials, self.serials)
        for value in modify_serials.values():
            self.assertEqual(value, self.date_now)

    def test_add(self):
        self.assertFalse('serial5' in self.serials)
        self.serials.add('serial5')
        self.assertTrue('serial5' in self.serials)

    def test_filter(self):
        # фильтрация без передачи ключа
        empty_filter = self.serials.filter()
        self.assertEqual(empty_filter, self.serials)
        none_filter = self.serials.filter(None)
        self.assertEqual(none_filter, self.serials)
        # фильтрация по ключу в разных регистрах
        equal_serial1_dict = {'Serial1': self.date_now}
        for key in ('serial1', 'Serial1', 'sERIAL1'):
            filter_by_key = self.serials.filter(key)
            self.assertEqual(filter_by_key, equal_serial1_dict)
        # фильтрация по неизвестному ключу
        filter_no_contains = self.serials.filter('serial_unknown')
        self.assertEqual(filter_no_contains, {})
        # фильтрация пустого набора
        self.assertEqual(UserSerials().filter(), {})
        self.assertEqual(UserSerials().filter('serial'), {})

    def test_group_by_date(self):
        group_by_date = tuple(self.serials.group_by_date())
        self.assertEqual(len(group_by_date), 3)
        self.assertEqual(len(group_by_date[0]), 2)

        self.serials.add('serial5')
        self.serials.add('serial6')
        group_by_date = tuple(self.serials.group_by_date())
        self.assertEqual(len(group_by_date), 4)
        last_date = self.date_now + timedelta(2)
        for date, serials in group_by_date:
            self.assertTrue(last_date > date)
            last_date = date
