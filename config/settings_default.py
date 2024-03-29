import os

import redis

from consts import RedisDatabases
from bots import BaseBot
from setup.dramatiq_config import configure_dramatiq
from setup.logging_config import configure_logging


class DefaultSettings:
    def __init__(self):
        self.ENV_NAME = os.getenv('ENV_NAME', 'localhost')
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
        self.HOST = os.environ.get('LOCAL_HOST', '0.0.0.0')  # адрес для запуска сервера uvicorn
        self.PORT = 8000  # порт для запуска сервера uvicorn
        # общедоступный адрес (если USE_NGROK = True, то PUBLIC_URL заменяется на выданный ngrok)
        public_host = os.environ.get('PUBLIC_HOST')
        public_port = os.environ.get('PUBLIC_PORT')  # Порт из списка 80, 88, 443, 8443
        self.PUBLIC_URL = f'https://{public_host}:{public_port}'
        # SSL
        self.SSL_PUBLIC_PATH = os.environ.get('SSL_PUBLIC_PATH')
        self.SSL_PRIVATE_PATH = os.environ.get('SSL_PRIVATE_PATH')

        self.LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {name} {lineno}: {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname} {asctime} {lineno}: {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'console': {
                    'level': 'INFO',
                    'formatter': 'verbose',
                    'class': 'logging.StreamHandler',
                },
                'admin_sender': {
                    'level': 'INFO',
                    'formatter': 'simple',
                    'class': 'management.logging_handlers.AdminHandler',
                },
            },
            'loggers': {
                'admin': {
                    'handlers': ['admin_sender'],
                    'level': 'INFO',
                },
            },
        }

    def post_init(self):
        configure_dramatiq(self.RABBITMQ_HOST)
        configure_logging(self.LOGGING)
