import os

import redis

from consts import RedisDatabases
from bots import BaseBot
from setup.dramatiq_config import configure_dramatiq
from setup.logging_config import configure_logging


class ProductionSettings:
    def __init__(self):
        self.ENV_NAME = 'PRODUCTION'
        self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        self.RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
        # хранилище для database.models
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

        # адрес локальной машины
        self.HOST = os.environ.get('LOCAL_HOST', '127.0.0.1')  # адрес для запуска сервера uvicorn
        self.PORT = 8000  # порт для запуска сервера uvicorn
        # общедоступный адрес - если USE_NGROK = True, то PUBLIC_URL заменяется на выданный ngrok
        self.PUBLIC_URL = os.environ.get('PUBLIC_URL', f'https://{self.HOST}')
        # SSL
        self.SSL_PUBLIC_PATH = os.environ.get('SSL_PUBLIC_PATH')
        self.SSL_PRIVATE_PATH = os.environ.get('SSL_PRIVATE_PATH')

    def post_init(self):
        configure_dramatiq(self.RABBITMQ_HOST)
        configure_logging()
