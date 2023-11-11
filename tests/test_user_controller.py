import asyncio
from unittest.mock import patch

from bots.admin_bot.controller import AdminController
from consts import MySeria, Zetflix
from database import ObjectNotFoundError
from database.models import User
from .base_test_case import DBTestCase


class UserControllerTest(DBTestCase):
    def test_get_user(self):
        asyncio.run()
