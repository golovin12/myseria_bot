import re

from aiogram import types, Router

from .controller import AdminController

router = Router()


@router.message(lambda message: re.fullmatch(r'^#new_addr: https?://.*$', message.text))
async def force_update_url(message: types.Message):
    """Команда для обновления адреса сайта вручную"""
    url = message.text.replace('#new_addr: ', '').rstrip(" /")
    result = await AdminController(message.from_user.id).force_update_my_seria_url(url)
    await message.reply(result)


@router.message(lambda message: message.text.startswith("#show_admins"))
async def show_admins(message: types.Message):
    """Команда для обновления адреса сайта вручную"""
    result = await AdminController(message.from_user.id).get_all_admins()
    await message.reply(result)


@router.message(lambda message: re.fullmatch(r'^#create_admin: \d*$', message.text))
async def create_admin(message: types.Message):
    """Добавление администратора"""
    admin_id = int(message.text.replace('#create_admin: ', ''))
    result = await AdminController(message.from_user.id).create_admin(admin_id)
    await message.reply(result)


@router.message(lambda message: re.fullmatch(r'^#delete_admin: \d*$', message.text))
async def delete_admin(message: types.Message):
    """Удаление администратора"""
    admin_id = int(message.text.replace('#delete_admin: ', ''))
    result = await AdminController(message.from_user.id).delete_admin(admin_id)
    await message.reply(result)
