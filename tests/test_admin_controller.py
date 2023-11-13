import asyncio
from unittest.mock import patch

from bots.admin_bot.controller import AdminController
from consts import MySeria, Zetflix
from database import ObjectNotFoundError
from database.models import Admin, SerialSite
from .base import DBMockTestCase


class AdminControllerTest(DBMockTestCase):
    def test_create_admin(self):
        admin_id = 2
        admin = asyncio.run(Admin.get_object(admin_id))
        self.assertFalse(admin.is_admin)
        asyncio.run(AdminController(1).create_admin(admin_id))
        admin = asyncio.run(Admin.get_object(admin_id))
        self.assertTrue(admin.is_admin)

    def test_delete_admin(self):
        # попытка удалить несуществующего админа
        asyncio.run(AdminController(3).delete_admin(999))
        # создание админа
        admin_id = 2
        asyncio.run(Admin(admin_id, True).save())
        admin = asyncio.run(Admin.get_object(admin_id))
        self.assertTrue(admin.is_admin)
        # попытка забрать роль администратора у себя
        asyncio.run(AdminController(admin_id).delete_admin(admin_id))
        admin = asyncio.run(Admin.get_object(admin_id))
        self.assertTrue(admin.is_admin)
        # забираем роль администратора у другого
        asyncio.run(AdminController(3).delete_admin(admin_id))
        admin = asyncio.run(Admin.get_object(admin_id))
        self.assertFalse(admin.is_admin)

    def test_get_all_admins(self):
        self.assertEqual(asyncio.run(AdminController(3).get_all_admins()), '')
        asyncio.run(Admin(2, True).save())
        asyncio.run(Admin(3, True).save())
        self.assertEqual(set(asyncio.run(AdminController(3).get_all_admins()).split('\n')), {'2', '3'})

    def test_update_my_seria_url(self):
        with patch('bots.admin_bot.controller.url_is_active') as mock_url_is_active:
            mock_url_is_active.return_value = True
            self.assertRaises(ObjectNotFoundError, asyncio.run, SerialSite.get_object(MySeria.KEY))
            # Попытка сохранить невалидный url
            asyncio.run(AdminController(3).force_update_my_seria_url('new_url'))
            self.assertRaises(ObjectNotFoundError, asyncio.run, SerialSite.get_object(MySeria.KEY))
            # Попытка сохранить неактивный url
            mock_url_is_active.return_value = False
            new_url = 'https://test_url.com'
            asyncio.run(AdminController(3).force_update_my_seria_url(new_url))
            self.assertRaises(ObjectNotFoundError, asyncio.run, SerialSite.get_object(MySeria.KEY))
            # Сохранение нового url
            mock_url_is_active.return_value = True
            asyncio.run(AdminController(3).force_update_my_seria_url(new_url))
            my_seria_site = asyncio.run(SerialSite.get_object(MySeria.KEY))
            self.assertEqual(my_seria_site.url, new_url)

    def test_update_zetflix_url(self):
        self.assertRaises(ObjectNotFoundError, asyncio.run, SerialSite.get_object(Zetflix.KEY))
        # Попытка сохранить невалидный url
        asyncio.run(AdminController(3).force_update_zetflix_url('new_url'))
        self.assertRaises(ObjectNotFoundError, asyncio.run, SerialSite.get_object(Zetflix.KEY))
        # Сохранение нового url
        new_url = 'https://test_url.com'
        asyncio.run(AdminController(3).force_update_zetflix_url(new_url))
        my_seria_site = asyncio.run(SerialSite.get_object(Zetflix.KEY))
        self.assertEqual(my_seria_site.url, new_url)
