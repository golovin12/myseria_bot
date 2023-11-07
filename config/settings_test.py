import os

import redis

from consts import RedisDatabases
from base_bot import BaseBot


class TestSettings:
    def __init__(self):
        self.ENV_NAME = 'TEST'
        self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        self._aioredis = None

        self.ADMIN_BOT_TOKEN = 'admin:bot_token'
        self.MY_SERIA_BOT_TOKEN = 'my_seria:bot_token'
        self.ZETFLIX_BOT_TOKEN = 'zetflix:bot_token'

        self.user_bots: dict[str, BaseBot] = {}

        self.ADMIN_ID = 111

        self.SECRET_TOKEN = 'secret'

        self.SKIP_UPDATES = True

        self.VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')

        self.USE_NGROK = False

        self.HOST = '127.0.0.1'
        self.PORT = 8000
        self.BASE_URL = f"https://{self.HOST}"

    @property
    def aioredis(self):
        # хранилище для database.models
        if self._aioredis is None or self._aioredis.connection is None:
            self._aioredis = redis.asyncio.Redis(host=self.REDIS_HOST, db=RedisDatabases.test, decode_responses=True)
        return self._aioredis