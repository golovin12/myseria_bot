import logging.config
import os

import dramatiq
import redis
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import AsyncIO

from consts import RedisDatabases
from bots import BaseBot


class ProductionSettings:
    def __init__(self):
        self.ENV_NAME = 'PROD'
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

        self.HOST = '127.0.0.1'
        self.PORT = 8000
        self.BASE_URL = f'https://{self.HOST}'  # если env.USE_NGROK = True, то BASE_URL заменяется на выданный ngrok

    def post_init(self):
        self._configure_dramatiq()
        self._configure_logging()

    def _configure_dramatiq(self):
        rabbitmq_broker = RabbitmqBroker(host=self.RABBITMQ_HOST, middleware=[AsyncIO()])
        dramatiq.set_broker(rabbitmq_broker)

    def _configure_logging(self):
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {name} {lineno} {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname} {name} {lineno} {message}',
                    'style': '{',
                },
                'django': {
                    'format': 'django: %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'level': 'INFO',
                    'formatter': 'verbose',
                    'class': 'logging.StreamHandler',
                },
                'file': {
                    'level': 'ERROR',
                    'formatter': 'verbose',
                    'class': 'logging.FileHandler',
                    'filename': 'py_log.log',
                },
                'admin_sender': {
                    'level': 'INFO',
                    'formatter': 'verbose',
                    'class': 'management.logging_handlers.AdminHandler',
                },
            },
            'loggers': {
                "admin": {
                    "handlers": ["admin_sender"],
                    "level": "INFO",
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": "INFO",
            },
        }

        logging.config.dictConfig(logging_config)
