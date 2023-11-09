import os
from pathlib import Path

from dotenv import load_dotenv

from .settings_production import ProductionSettings
from .settings_test import TestSettings

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(f'{BASE_DIR}/.env')

settings = ProductionSettings() if os.getenv("ENV_NAME") != "TEST" else TestSettings()

__all__ = ('settings',)
