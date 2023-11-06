import os

import redis

from consts import RedisDatabases
from base_bot import BaseBot


class ProductionSettings:
    def __init__(self):
        self.ENV_NAME = 'PROD'
        self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        self.aioredis = redis.asyncio.Redis(host=self.REDIS_HOST, db=RedisDatabases.default, decode_responses=True)

        self.ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN', '')
        self.MY_SERIA_BOT_TOKEN = os.getenv('MY_SERIA_BOT_TOKEN', '')
        self.ZETFLIX_BOT_TOKEN = os.getenv('ZETFLIX_BOT_TOKEN', '')

        self.user_bots: dict[str, BaseBot] = {}

        self.ADMIN_ID = os.getenv('ADMIN_ID', '')

        self.SECRET_TOKEN = os.getenv('SECRET_TOKEN')

        self.SKIP_UPDATES = os.environ.get('SKIP_UPDATES', 'True') == 'True'

        self.VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')

        self.USE_NGROK = os.environ.get('USE_NGROK', 'False') == 'True'

        self.HOST = '127.0.0.1'
        self.PORT = 8000
        self.BASE_URL = f'https://{self.HOST}'  # если env.USE_NGROK = True, то BASE_URL заменяется на выданный ngrok
