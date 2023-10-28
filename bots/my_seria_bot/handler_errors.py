from aiogram import Router, F
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message

from database.errors import ObjectNotFoundError

router = Router()


@router.error(ExceptionTypeFilter(ObjectNotFoundError), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message):
    await message.answer("Не удалось получить запись из бд")
