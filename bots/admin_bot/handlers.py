import re

from aiogram import types, Router

from .consts import ControlCommand
from .controller import AdminController

router = Router()


@router.message(lambda message: message.text == ControlCommand.HELP)
async def command_help(message: types.Message):
    """Доступные методы"""
    await message.reply(ControlCommand.all_commands)


@router.message(lambda message: re.fullmatch(rf'^{ControlCommand.NEW_ADDR}$', message.text))
async def force_update_url(message: types.Message):
    """Команда для обновления адреса сайта вручную"""
    url = message.text.replace('#new_addr: ', '').rstrip(" /")
    result = await AdminController(message.from_user.id).force_update_my_seria_url(url)
    await message.reply(result)


@router.message(lambda message: message.text.startswith(ControlCommand.SHOW_ADMINS))
async def show_admins(message: types.Message):
    """Команда для обновления адреса сайта вручную"""
    result = await AdminController(message.from_user.id).get_all_admins()
    await message.reply(result)


@router.message(lambda message: re.fullmatch(rf'^{ControlCommand.CREATE_ADMIN}$', message.text))
async def create_admin(message: types.Message):
    """Добавление администратора"""
    admin_id = int(message.text.replace('#create_admin: ', ''))
    result = await AdminController(message.from_user.id).create_admin(admin_id)
    await message.reply(result)


@router.message(lambda message: re.fullmatch(rf'^{ControlCommand.DELETE_ADMIN}$', message.text))
async def delete_admin(message: types.Message):
    """Удаление администратора"""
    admin_id = int(message.text.replace('#delete_admin: ', ''))
    result = await AdminController(message.from_user.id).delete_admin(admin_id)
    await message.reply(result)
