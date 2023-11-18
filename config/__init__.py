import os
from pathlib import Path

from dotenv import load_dotenv

from .settings_production import ProductionSettings
from .settings_test import TestSettings

BASE_DIR = Path(__file__).resolve().parent.parent

env_name = os.getenv('ENV_NAME')
if env_name == 'TEST':
    # тестовое окружение
    settings = TestSettings()
else:
    env_file_name = '.env.dev'
    if env_name == 'DOCKER':
        # окружение для запуска через docker-compose без ngrok
        env_file_name = '.env.docker'
    elif env_name == 'LOCAL':
        # окружение для запуска на локальной машине без ngrok
        env_file_name = '.env.local'
    load_dotenv(f'{BASE_DIR}/management/envs/.env.base')  # токены, секретные ключи (чтобы не дублировать)
    load_dotenv(f'{BASE_DIR}/management/envs/{env_file_name}')  # отличающиеся переменные
    settings = ProductionSettings()

settings.post_init()

__all__ = ('settings',)
