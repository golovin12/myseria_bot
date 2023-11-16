import logging

from config import settings
from bots.admin_bot.tasks import admin_bot_send_message


class AdminHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        admin_bot_send_message.send(settings.ADMIN_ID, record.getMessage())
