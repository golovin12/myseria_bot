import asyncio
import warnings
from collections import UserDict
from datetime import datetime
from unittest import TestCase

from database import ObjectNotFoundError
from database.fields import ValidateField, CharField, UrlField, PositiveIntegerField, BooleanField, JsonField
from database.models import SerialSite, User, Admin
from .base_test_case import DBTestCase


class MyBaseClass:
    field: ValidateField

    def set_field_value(self, value):
        self.field = value


class DatabaseFieldsTest(TestCase):
    def test_pk_fields(self):
        class MyClass(MyBaseClass):
            field = CharField(is_pk=True)

        test_instance = MyClass()
        test_instance.field = 'test'
        self.assertRaises(AttributeError, test_instance.set_field_value, 'test2')

        class MyClass(MyBaseClass):
            field = CharField(is_pk=False)

        test_instance = MyClass()
        test_instance.field = 'test'
        test_instance.set_field_value('test2')
        self.assertEqual(test_instance.field, 'test2')

    def test_char_field(self):
        class MyClass(MyBaseClass):
            field = CharField(empty_allowed=True)

        test_instance = MyClass()
        test_instance.field = 'test'
        self.assertEqual(test_instance.field, 'test')
        test_instance.field = '  test2  '
        self.assertEqual(test_instance.field, 'test2')
        test_instance.field = ''
        self.assertEqual(test_instance.field, '')
        test_instance.field = '    '
        self.assertEqual(test_instance.field, '')
        self.assertRaises(ValueError, test_instance.set_field_value, None)
        self.assertRaises(ValueError, test_instance.set_field_value, 1)
        self.assertRaises(ValueError, test_instance.set_field_value, test_instance)

        class MyClass(MyBaseClass):
            field = CharField(empty_allowed=False)

        test_instance = MyClass()
        test_instance.field = 'test'
        self.assertEqual(test_instance.field, 'test')
        self.assertRaises(ValueError, test_instance.set_field_value, '')
        self.assertRaises(ValueError, test_instance.set_field_value, '     ')

    def test_url_field(self):
        class MyClass(MyBaseClass):
            field = UrlField()

        test_instance = MyClass()
        test_instance.field = 'http://test.com'
        self.assertEqual(test_instance.field, 'http://test.com')
        test_instance.field = 'https://test2.com/   '
        self.assertEqual(test_instance.field, 'https://test2.com')
        self.assertRaises(ValueError, test_instance.set_field_value, 'url')
        self.assertRaises(ValueError, test_instance.set_field_value, 'https://test.com/serials')
        self.assertRaises(ValueError, test_instance.set_field_value, 'https://test.com//')
        self.assertRaises(ValueError, test_instance.set_field_value, None)
        self.assertRaises(ValueError, test_instance.set_field_value, 1)
        self.assertRaises(ValueError, test_instance.set_field_value, test_instance)

    def test_positive_integer_field(self):
        class MyClass(MyBaseClass):
            field = PositiveIntegerField()

        test_instance = MyClass()
        test_instance.field = 0
        self.assertEqual(test_instance.field, 0)
        test_instance.field = (9 ** 10)
        self.assertEqual(test_instance.field, 9 ** 10)
        self.assertRaises(ValueError, test_instance.set_field_value, -1)
        self.assertRaises(ValueError, test_instance.set_field_value, None)
        self.assertRaises(ValueError, test_instance.set_field_value, 1.1)
        self.assertRaises(ValueError, test_instance.set_field_value, test_instance)

    def test_boolean_field(self):
        class MyClass(MyBaseClass):
            field = BooleanField()

        test_instance = MyClass()
        test_instance.field = False
        self.assertEqual(test_instance.field, False)
        test_instance.field = True
        self.assertEqual(test_instance.field, True)
        self.assertRaises(ValueError, test_instance.set_field_value, 0)
        self.assertRaises(ValueError, test_instance.set_field_value, None)
        self.assertRaises(ValueError, test_instance.set_field_value, test_instance)

    def test_json_field(self):
        class MyClass(MyBaseClass):
            field = JsonField()

        test_instance = MyClass()
        test_instance.field = {}
        self.assertEqual(test_instance.field, {})
        self.assertIsInstance(test_instance.field, dict)
        test_instance.field = UserDict(test='test')
        self.assertEqual(test_instance.field, {'test': 'test'})
        self.assertIsInstance(test_instance.field, UserDict)
        self.assertRaises(ValueError, test_instance.set_field_value, None)
        self.assertRaises(ValueError, test_instance.set_field_value, test_instance)

        class MyClass(MyBaseClass):
            field = JsonField(user_type=UserDict)

        test_instance = MyClass()
        test_instance.field = {'test': 'test'}
        self.assertEqual(test_instance.field, {'test': 'test'})
        self.assertIsInstance(test_instance.field, UserDict)
        test_instance.field = UserDict()
        self.assertEqual(test_instance.field, {})
        self.assertIsInstance(test_instance.field, UserDict)
        self.assertRaises(ValueError, test_instance.set_field_value, None)
        self.assertRaises(ValueError, test_instance.set_field_value, test_instance)


class DatabaseModelsTest(DBTestCase):
    def test_serials_site(self):
        warnings.simplefilter("ignore", ResourceWarning)
        serial_site = SerialSite('name', 'https://test')
        # попытка инициализации объекта с невалидными значениями
        self.assertRaises(ValueError, SerialSite, '', '')
        self.assertRaises(ValueError, SerialSite, 'name', '')
        self.assertRaises(ValueError, SerialSite, '', 'https://test')
        # попытка получения объекта по невалидному ключу
        invalid_obj = SerialSite.get_object('')
        self.assertRaises(ObjectNotFoundError, asyncio.run, invalid_obj)
        # попытка получения объекта из бд, который ещё не создан
        obj_not_found = SerialSite.get_object(serial_site.name)
        self.assertRaises(ObjectNotFoundError, asyncio.run, obj_not_found)
        # получение из бд объекта, который был сохранён
        asyncio.run(serial_site.save())
        obj_from_bd = asyncio.run(SerialSite.get_object(serial_site.name))
        self.assertEqual(obj_from_bd.name, serial_site.name)
        self.assertEqual(obj_from_bd.url, serial_site.url)
        # изменение значений
        self.assertRaises(AttributeError, setattr, obj_from_bd, 'name', 'name2')
        obj_from_bd.url = 'https://test2/ '
        asyncio.run(obj_from_bd.save())
        obj_from_bd = asyncio.run(SerialSite.get_object(serial_site.name))
        self.assertEqual(obj_from_bd.url, 'https://test2')

    def test_user(self):
        warnings.simplefilter("ignore", ResourceWarning)
        datetime_now = datetime.now()
        user = User(1, {'serial': datetime_now.strftime("%d.%m.%Y")})
        # попытка инициализации объекта с невалидными значениями
        self.assertRaises(ValueError, User, 1, None)
        self.assertRaises(ValueError, User, None, {})
        self.assertRaises(ValueError, User, 1, {'serial': 'text'})
        self.assertRaises(ValueError, User, -1, {'serial': datetime_now})
        # попытка получения объекта по невалидному ключу
        invalid_obj = User.get_object(-1)
        self.assertRaises(ObjectNotFoundError, asyncio.run, invalid_obj)
        # попытка получения объекта из бд, который ещё не создан
        default_obj = asyncio.run(User.get_object(user.user_id))
        self.assertEqual(default_obj.user_id, user.user_id)
        self.assertEqual(default_obj.serials, {})
        self.assertNotEqual(default_obj.serials, user.serials)
        # получение из бд объекта, который был сохранён
        asyncio.run(user.save())
        obj_from_bd = asyncio.run(User.get_object(user.user_id))
        self.assertEqual(obj_from_bd.user_id, user.user_id)
        self.assertEqual(obj_from_bd.serials, user.serials)
        # изменение значений
        self.assertRaises(AttributeError, setattr, obj_from_bd, 'user_id', 2)
        obj_from_bd.serials = {'serial2': datetime_now}
        asyncio.run(obj_from_bd.save())
        obj_from_bd = asyncio.run(User.get_object(user.user_id))
        self.assertEqual(obj_from_bd.serials, {'Serial2': datetime(day=datetime_now.day,
                                                                   month=datetime_now.month,
                                                                   year=datetime_now.year)})

    def test_admin(self):
        warnings.simplefilter("ignore", ResourceWarning)
        admin = Admin(1, True)
        # попытка инициализации объекта с невалидными значениями
        self.assertRaises(ValueError, Admin, 1, None)
        self.assertRaises(ValueError, Admin, None, True)
        # попытка получения объекта по невалидному ключу
        invalid_obj = Admin.get_object(-1)
        self.assertRaises(ObjectNotFoundError, asyncio.run, invalid_obj)
        # попытка получения объекта из бд, который ещё не создан
        default_obj = asyncio.run(Admin.get_object(admin.user_id))
        self.assertEqual(default_obj.user_id, admin.user_id)
        self.assertEqual(default_obj.is_admin, False)
        self.assertNotEqual(default_obj.is_admin, admin.is_admin)
        # получение из бд объекта, который был сохранён
        asyncio.run(admin.save())
        obj_from_bd = asyncio.run(Admin.get_object(admin.user_id))
        self.assertEqual(obj_from_bd.user_id, admin.user_id)
        self.assertEqual(obj_from_bd.is_admin, admin.is_admin)
        # изменение значений
        self.assertRaises(AttributeError, setattr, obj_from_bd, 'user_id', 2)
        obj_from_bd.is_admin = False
        asyncio.run(obj_from_bd.save())
        obj_from_bd = asyncio.run(Admin.get_object(admin.user_id))
        self.assertEqual(obj_from_bd.is_admin, False)
        # Получение списка администраторов
        admins_id = asyncio.run(Admin.get_admins_id())
        self.assertEqual(admins_id, set())
        admin2 = Admin(2, True)
        asyncio.run(admin2.save())
        admins_id = asyncio.run(Admin.get_admins_id())
        self.assertEqual(admins_id, {f'{admin2.user_id}'})
