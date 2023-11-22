import os
from pathlib import Path

from dotenv import load_dotenv

from .settings_docker import DockerSettings
from .settings_local import LocalSettings
from .settings_test import TestSettings

BASE_DIR = Path(__file__).resolve().parent.parent

env_name = os.getenv('ENV_NAME')
if env_name == 'TEST':
    # тестовое окружение
    settings = TestSettings()
else:
    match env_name:
        case 'DOCKER':
            env_file_name = '.env.docker'
            settings_class = DockerSettings
        case 'LOCAL':
            env_file_name = '.env.local'
            settings_class = LocalSettings
        case _:
            env_file_name = '.env.dev'
            settings_class = LocalSettings
    load_dotenv(f'{BASE_DIR}/management/envs/.env.base')  # токены, секретные ключи (чтобы не дублировать)
    load_dotenv(f'{BASE_DIR}/management/envs/{env_file_name}')  # отличающиеся переменные
    settings = settings_class()

settings.post_init()

__all__ = ('settings',)
