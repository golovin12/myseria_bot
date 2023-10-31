import logging

from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent

from database import ObjectNotFoundError
from serial_services import ParsingError
from .handler import BaseHandler

logger = logging.getLogger(__name__)


class ErrorsHandler(BaseHandler):
    def register_first(self):
        self.dp.error(ExceptionTypeFilter(ObjectNotFoundError))(self.object_not_found_exception)
        self.dp.error(ExceptionTypeFilter(ParsingError))(self.parsing_exception)

    async def object_not_found_exception(self, event: ErrorEvent):
        logger.exception(event.exception)
        print(event.exception)

    async def parsing_exception(self, event: ErrorEvent):
        logger.exception(event.exception)
        print(event.exception)
