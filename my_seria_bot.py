import asyncio

import redis
from aiogram import Bot, types, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.markdown import hlink

from consts import ControlCommand
from my_seria_parcer import (
    force_update_address, get_user_new_series, get_user_serials, user_add_serial, create_user_if_not_exist,
    user_delete_serial, set_user_serials, get_serial_info
)
from token_bot import token_bot
from utils import list_separator, ButtonPaginator

TOKEN = token_bot.TOKEN  # todo to Env
storage = RedisStorage(redis.asyncio.Redis(db=5))  # todo pool_size=10, prefix='my_fsm_key'
dp = Dispatcher(storage=storage)


class UserState(StatesGroup):
    new_series = State()
    add_serials = State()
    delete_serials = State()
    my_serials = State()


@dp.message(Command(ControlCommand.START))
async def command_start(message: types.Message):
    """Приветствие"""
    print(f"start command: {message.from_user.id}")
    await create_user_if_not_exist(message.from_user.id)
    buttons = [types.KeyboardButton(text=f"/{command}") for command, name in ControlCommand.choices]
    buttons = list_separator(buttons, 2)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите команду"
    )
    await message.reply(
        "Привет, данный бот предназначен для отслеживания выхода серий с сайта MySeria.\n"
        "Вы можете создать свой список для отслеживания сериалов и получать актуальную информацию о новых сериях.\n"
        "Также данный бот может показать вышедшие озвучки для конкретной серии.\n"
        f"Список команд, для работы с ботом представлен ниже:\n{ControlCommand.all_commands}",
        reply_markup=keyboard)


@dp.message(Command(ControlCommand.HELP))
async def command_help(msg: types.Message):
    """Список возможных команд"""
    await msg.reply(f"Список доступных команд:\n{ControlCommand.all_commands}")


@dp.message(lambda message: message.text.lower().startswith("#new_addr: "))
async def force_update_url(message: types.Message):
    """Команда для обновления адреса сайта вручную"""
    # todo сделать доступ этой к команде только для админов
    url = message.text.replace('#new_addr: ', '')
    is_complete = await force_update_address(url)
    if is_complete:
        await message.reply(f'Адрес успешно обновлён на: {url}')
    else:
        await message.reply('Не удалось обновить адрес')


@dp.message(Command(ControlCommand.CANCEL))
@dp.message(F.text.lower() == 'отмена')
async def command_cancel(message: types.Message, state: FSMContext):
    """Отмена операции и сброс любого состояния"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    await message.reply('Операция отменена')


@dp.message(Command(ControlCommand.REBOOT))
async def add_serials_command(message: types.Message):
    """Сбрасывает список отслеживаемых сериалов"""
    await set_user_serials(message.from_user.id, {})
    await message.reply("Информация о Вас успешно сброшена.")


@dp.callback_query(UserState.new_series, F.data.startswith("#page-"))
@dp.callback_query(UserState.delete_serials, F.data.startswith("#page-"))
@dp.callback_query(UserState.my_serials, F.data.startswith("#page-"))
async def paginate_serials(callback_query: types.CallbackQuery, state: FSMContext):
    # Обновление клавиатуры при пагинации
    await callback_query.answer()
    data = await state.get_data()
    serials = await get_user_serials(callback_query.from_user.id)
    paginator = ButtonPaginator(data['btn_name'], data['btn_callback'], "#page-")
    keyboard = paginator.get_paginated_keyboard(serials, callback_query.data)
    await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=keyboard)


@dp.message(Command(ControlCommand.NEW_SERIES))
async def command_new_series(message: types.Message, state: FSMContext):
    """Получить информацию о новых сериях"""
    await state.set_state(UserState.new_series)
    serials = await get_user_serials(message.from_user.id)
    btn_name, btn_callback = 'Все новые серии', '__all__'
    await state.update_data(btn_name=btn_name, btn_callback=btn_callback)
    keyboard = ButtonPaginator(btn_name, btn_callback).get_paginated_keyboard(serials)
    await message.reply("Выберите сериал, по которому хотите получить новинки", reply_markup=keyboard)


@dp.message(Command(ControlCommand.ADD_SERIALS))
async def command_add_serials(message: types.Message, state: FSMContext):
    await state.set_state(UserState.add_serials)
    await message.reply("Отправляйте боту названия сериалов, которые хотите добавить (по одному):")


@dp.message(Command(ControlCommand.DELETE_SERIALS))
async def command_delete_serials(message: types.Message, state: FSMContext):
    await state.set_state(UserState.delete_serials)
    serials = await get_user_serials(message.from_user.id)
    btn_name, btn_callback = 'Выход из удаления', '__exit__'
    await state.update_data(btn_name=btn_name, btn_callback=btn_callback)
    keyboard = ButtonPaginator(btn_name, btn_callback).get_paginated_keyboard(serials)
    await message.reply("Выберите сериал, который хотите удалить", reply_markup=keyboard)


@dp.message(Command(ControlCommand.MY_SERIALS))
async def command_my_serials(message: types.Message, state: FSMContext):
    serials = await get_user_serials(user_id=message.from_user.id)
    if not serials:
        await message.reply("Вы ещё не добавили сериалы для отслеживания. Чтобы добавить, нажмите: /add_serials")
        return
    await state.set_state(UserState.my_serials)
    btn_name, btn_callback = 'Закрыть', '__exit__'
    await state.update_data(btn_name=btn_name, btn_callback=btn_callback)
    keyboard = ButtonPaginator(btn_name, btn_callback).get_paginated_keyboard(serials)
    await message.reply(
        "Ниже представлен список выбранных тобой сериалов, выбери о каком из них хочешь получить информацию.",
        reply_markup=keyboard)


@dp.callback_query(UserState.new_series)
async def get_new_series(callback_query: types.CallbackQuery, state: FSMContext):
    """Получение информации о новых сериях"""
    await state.clear()
    await callback_query.answer("Подождите, информация собирается...")
    await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
    serial = callback_query.data
    async for seria_info in get_user_new_series(callback_query.from_user.id, serial):
        await callback_query.message.answer(seria_info)


@dp.message(UserState.add_serials)
async def add_serial(message: types.Message):
    """Добавление сериала в список отслеживания"""
    serial = message.text.strip()
    await message.reply("Подождите, сериал проверяется...")
    result_text = await user_add_serial(message.from_user.id, serial)
    await message.answer(result_text)


@dp.callback_query(UserState.delete_serials)
async def delete_serial(callback_query: types.CallbackQuery, state: FSMContext):
    """Удаление сериала из списка отслеживания"""
    await callback_query.answer()
    if callback_query.data == '__exit__':
        await state.clear()
        await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
        return
    data = await state.get_data()
    paginator = ButtonPaginator(data['btn_name'], data['btn_callback'], "#page-")
    serial = callback_query.data.strip()
    result_text, is_deleted = await user_delete_serial(callback_query.from_user.id, serial)
    if is_deleted:
        serials = await get_user_serials(callback_query.from_user.id)
        keyboard = paginator.get_paginated_keyboard(serials, callback_query.data)
        await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=keyboard)
    await callback_query.message.answer(result_text)


@dp.callback_query(UserState.my_serials)
async def serial_info(callback_query: types.CallbackQuery, state: FSMContext):
    """Получение актуальной информации о сериале"""
    await callback_query.answer()
    if callback_query.data == '__exit__':
        await state.clear()
        await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
        return
    serial = callback_query.data.strip()
    info = get_serial_info(serial)  # todo async
    await callback_query.message.answer(
        f'<b>Информация о сериале:</b> \n{hlink(info["name"], info["url"])}\n'
        f'<b>Количество сезонов:</b> {info["num_season"]}\n'
        f'<b>Последняя серия:</b> \n{hlink(info["last_seria_name"], info["last_seria_url"])}\n'
        f'<b>Дата выхода серии:</b> \n{info["date"]}\n'
        f'<b>Вышедшие озвучки:</b> \n{", ".join(info["voices"])}\n',
        disable_web_page_preview=True
    )


@dp.shutdown()
async def shutdown():
    try:
        await dp.storage.close()
    except Exception as e:
        print(e)


async def main():
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
