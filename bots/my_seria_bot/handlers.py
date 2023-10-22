from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils import message_per_seconds_limiter
from .consts import ControlCommand, CallbackButtonInfo
from .controller import UserController
from .keyboards import get_main_keyboard, get_paginated_serials_keyboard
from .states import UserState

router = Router()


@router.message(Command(ControlCommand.START))
async def command_start(message: types.Message):
    """Приветствие"""
    await message.reply(
        "Привет, данный бот предназначен для отслеживания выхода серий с сайта MySeria.\n"
        "Вы можете создать свой список для отслеживания сериалов и получать актуальную информацию о новых сериях.\n"
        "Также данный бот может показать вышедшие озвучки для конкретной серии.\n"
        f"Список команд, для работы с ботом представлен ниже:\n{ControlCommand.all_commands}",
        reply_markup=get_main_keyboard())


@router.message(Command(ControlCommand.HELP))
async def command_help(msg: types.Message):
    """Список возможных команд"""
    await msg.reply(f"Список доступных команд:\n{ControlCommand.all_commands}")


@router.message(Command(ControlCommand.CANCEL))
@router.message(F.text.lower() == 'отмена')
async def command_cancel(message: types.Message, state: FSMContext):
    """Отмена операции и сброс любого состояния"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    await message.reply('Операция отменена')


@router.message(Command(ControlCommand.REBOOT))
async def add_serials_command(message: types.Message):
    """Сбрасывает список отслеживаемых сериалов"""
    await UserController(message.from_user.id).reboot()
    await message.reply("Информация о Вас успешно сброшена.")


@router.message(Command(ControlCommand.NEW_SERIES))
async def command_new_series(message: types.Message, state: FSMContext):
    """Получить информацию о новых сериях"""
    await state.set_state(UserState.new_series)
    serials = await UserController(message.from_user.id).get_serials()
    keyboard = await get_paginated_serials_keyboard(serials, state, CallbackButtonInfo.ALL)
    await message.reply("Выберите сериал, по которому хотите получить новинки", reply_markup=keyboard)


@router.message(Command(ControlCommand.ADD_SERIALS))
async def command_add_serials(message: types.Message, state: FSMContext):
    await state.set_state(UserState.add_serials)
    await message.reply("Отправляйте боту названия сериалов, которые хотите добавить (по одному):")


@router.message(Command(ControlCommand.DELETE_SERIALS))
async def command_delete_serials(message: types.Message, state: FSMContext):
    await state.set_state(UserState.delete_serials)
    serials = await UserController(message.from_user.id).get_serials()
    keyboard = await get_paginated_serials_keyboard(serials, state, CallbackButtonInfo.CLOSE)
    await message.reply("Выберите сериал, который хотите удалить", reply_markup=keyboard)


@router.message(Command(ControlCommand.MY_SERIALS))
async def command_my_serials(message: types.Message, state: FSMContext):
    serials = await UserController(message.from_user.id).get_serials()
    if not serials:
        await message.reply("Вы ещё не добавили сериалы для отслеживания. Чтобы добавить, нажмите: /add_serials")
        return
    await state.set_state(UserState.my_serials)
    keyboard = await get_paginated_serials_keyboard(serials, state, CallbackButtonInfo.CLOSE)
    await message.reply(
        "Ниже представлен список выбранных тобой сериалов, выбери о каком из них хочешь получить информацию.",
        reply_markup=keyboard)


@router.callback_query(UserState.new_series)
async def get_new_series(callback_query: types.CallbackQuery, state: FSMContext):
    """Получение информации о новых сериях"""
    await state.clear()
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
    await callback_query.message.answer("Подождите, информация собирается...")
    serial_name = callback_query.data
    if serial_name == CallbackButtonInfo.ALL:
        new_series = UserController(callback_query.from_user.id).get_new_series()
    else:
        new_series = UserController(callback_query.from_user.id).get_new_series(serial_name)
    async for seria_info in message_per_seconds_limiter(new_series):
        await callback_query.message.answer(seria_info)


@router.message(UserState.add_serials)
async def add_serial(message: types.Message):
    """Добавление сериала в список отслеживания"""
    serial_name = message.text.strip()
    await message.reply("Подождите, сериал проверяется...")
    is_added = await UserController(message.from_user.id).add_serial(serial_name)
    if is_added:
        await message.answer(
            f"Сериал {serial_name} был успешно добавлен!\nМожете указать название другого сериала для добавления."
        )
    else:
        await message.answer(
            f"Не удалось добавить сериал {serial_name} (убедитесь, что сериал с таким названием есть на сайте MySeria)"
        )


@router.callback_query(UserState.delete_serials)
async def delete_serial(callback_query: types.CallbackQuery, state: FSMContext):
    """Удаление сериала из списка отслеживания"""
    await callback_query.answer()
    if callback_query.data == CallbackButtonInfo.CLOSE:
        await state.clear()
        await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
        return
    serial_name = callback_query.data.strip()
    user_controller = UserController(callback_query.from_user.id)
    is_deleted = await user_controller.delete_serial(serial_name)
    if is_deleted:
        serials = await user_controller.get_serials()
        keyboard = await get_paginated_serials_keyboard(serials, state, CallbackButtonInfo.CLOSE)
        await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=keyboard)
        await callback_query.message.answer(
            f"Сериал {serial_name} был успешно удален!\nМожете выбрать ещё сериал для удаления."
        )
    else:
        await callback_query.message.answer(
            f"Не удалось удалить сериал {serial_name}, возможно он отсутствует в списке отслеживаемых сериалов"
        )


@router.callback_query(UserState.my_serials)
async def serial_info(callback_query: types.CallbackQuery, state: FSMContext):
    """Получение актуальной информации о сериале"""
    await callback_query.answer('Подождите, информация собирается...')
    if callback_query.data == CallbackButtonInfo.CLOSE:
        await state.clear()
        await callback_query.message.edit_reply_markup(callback_query.inline_message_id, reply_markup=None)
        return
    serial_name = callback_query.data.strip()
    info = await UserController(callback_query.from_user.id).get_serial_info(serial_name)
    await callback_query.message.answer(info, disable_web_page_preview=True)
