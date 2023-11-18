import logging

from config import settings
from bots.admin_bot.tasks import admin_bot_send_message


class AdminHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        admin_id = settings.ADMIN_ID
        if admin_id:
            admin_bot_send_message.send(admin_id, self.format(record))
