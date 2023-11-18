import redis

from consts import RedisDatabases
from bots import BaseBot


class TestSettings:
    def __init__(self):
        self.ENV_NAME = 'TEST'
        self.REDIS_HOST = 'localhost'
        self.RABBITMQ_HOST = 'localhost'
        # хранилище для database.models
        self._aioredis = None

        self.ADMIN_BOT_TOKEN = 'admin:bot_token'
        self.MY_SERIA_BOT_TOKEN = 'my_seria:bot_token'
        self.ZETFLIX_BOT_TOKEN = 'zetflix:bot_token'

        self._user_bots: dict[str, BaseBot] = {}

        self.ADMIN_ID = 111

        self.SECRET_TOKEN = 'secret'

        self.SKIP_UPDATES = True

        self.VK_ACCESS_TOKEN = 'vk_token'

        self.USE_NGROK = False

        self.HOST = '127.0.0.1'
        self.PORT = 8000
        self.PUBLIC_URL = f"https://{self.HOST}"
        # SSL
        self.SSL_PUBLIC_PATH = None
        self.SSL_PRIVATE_PATH = None

    @property
    def user_bots(self):
        return self._user_bots

    @property
    def aioredis(self):
        # в тестах соединение закрывается, и приходится его заново открывать
        if self._aioredis is None or self._aioredis.connection is None:
            self._aioredis = redis.asyncio.Redis(host=self.REDIS_HOST, db=RedisDatabases.test, decode_responses=True)
        return self._aioredis

    def post_init(self):
        pass
