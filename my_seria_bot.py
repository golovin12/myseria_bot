import asyncio
from asyncio import sleep
from datetime import datetime, timedelta

import redis
from aiogram import Bot, types, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hlink

from my_seria_parcer import refactor_serials, user_info, serial_info, user_news, reboot, force_update_address
from token_bot import token_bot

TOKEN = token_bot.TOKEN
storage = RedisStorage(redis.asyncio.Redis(db=5))  # todo
dp = Dispatcher(storage=storage)
date_spisok = ["last_week", "last_month", "last_3month", "last_year", "last_day", "date", "my"]
date_spisok2 = ["Последняя неделя", "Последний месяц", "Последние 3 месяца", "Последний год", "Последние N дней",
                "Своя дата", "Последний запрос"]


# создаём форму и указываем поля
class Form_serial(StatesGroup):
    serials = State()
    command = State()


class Form_date(StatesGroup):
    publish_date = State()


# Приветствие
@dp.message(Command('start'))
async def start_command(msg: types.Message):
    try:
        refactor_serials(msg.from_user.id, "", None)
        buttons = [
            [
                types.KeyboardButton(text="/add_serials"),
                types.KeyboardButton(text="/my_serials"),
            ],
            [
                types.KeyboardButton(text="/delete_serials"),
                types.KeyboardButton(text="/serials_news"),
            ],
            [
                types.KeyboardButton(text="/help"),
            ],
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            input_field_placeholder="Выберите команду"
        )
        await msg.reply(
            "Привет, данный бот предназначен для отслеживания выхода серий с сайта MySeria.\n"
            "Вы можете ввести названия сериалов, которые бот будет отслеживать.\n"
            "Для каждого сериала можете выбрать число, с которого нужно отслеживать выход серий.\n"
            "Также данный бот может показать вышедшие озвучки для конкретной серии.\n"
            "Для того, чтобы добавить сериалы в список для отслеживания, введите команду: /add_serials\n"
            "Для того, чтобы удалить сериалы из списка для отслеживания, введите команду: /delete_serials\n"
            "Для того, чтобы получить информацию по сериалам, введите команду: /my_serials\n"
            "Для того, чтобы узнать о выходе новых серий, введите команду: /serials_news\n"
            "Для того, чтобы обнулить список сериалов для отслеживания, введите команду: /reboot\n"
            "Для того, чтобы увидеть список возможных команд, введите команду: /help\n",
            reply_markup=keyboard)
    except Exception as e:
        print(e)


# Список возможных команд
@dp.message(Command('help'))
async def start_command(msg: types.Message):
    try:
        await msg.reply(
            "Список доступных команд:\n"
            "/start - Приветствие\n"
            "/help - Список команд\n"
            "/add_serials - Добавить сериалы для отслеживания\n"
            "/delete_serials - Убрать сериалы из отслеживания\n"
            "/my_serials - Получение информации по отдельным сериалам\n"
            "/serials_news - Получить информацию о вышедших сериалах за последнее время\n"
            "/reboot - Сбросить весь список сериалов\n"
            'Введите: "##new_addr: url" Чтобы обновить адрес сайта (если он не работает)'
        )
    except Exception as e:
        print(e)


# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message(Command('cancel'))
@dp.message(F.text.lower() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.clear()
        await message.reply('ОК')
    except Exception as e:
        print(e)


@dp.message(lambda message: message.text.lower().startswith("#new_addr: "))
async def force_update_url(message: types.Message):
    try:
        url = message.text.replace('#new_addr: ', '')
        is_complete = force_update_address(url)
        if is_complete:
            await message.reply(f'Адрес успешно обновлён на: {url}')
        else:
            await message.reply('Не удалось обновить адрес')
    except Exception as e:
        print(e)


# Выводит информацию о последних сериях
@dp.message(Command('serials_news'))
async def add_serials_command(message: types.Message):
    try:
        keyboard_builder = InlineKeyboardBuilder()
        for i in range(len(date_spisok)):
            keyboard_builder.add(types.InlineKeyboardButton(
                text=date_spisok2[i],
                callback_data=f"serial_news {i}")
            )
        await message.reply("Выберите, за какую дату вы хотите получить информацию:",
                            reply_markup=keyboard_builder.as_markup())
    except Exception as e:
        print(e)


@dp.callback_query(lambda callback_query: callback_query.data.lower().startswith("serial_news"))
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        date = callback_query.data[12:]
        if date in ["0", "1", "2", "3", "6"]:
            await callback_query.message.answer("Подождите, собирается информация...")
            await callback_query.answer()
            serials = user_news(callback_query.from_user.id, date_spisok[int(date)])
            if len(serials) == 0:
                await callback_query.message.answer("Новинок нет.")
            elif serials == "Пусто":
                await callback_query.message.answer("Вы ещё не добавили ни один фильм.")
            else:
                dict_keys = sorted(serials.keys())
                speed = 0
                for i in dict_keys:
                    serial = serials.get(i)
                    await callback_query.message.answer(f"<b>Сериал:\n{i}</b>")
                    for seria in serial:
                        if speed % 10 == 0:
                            await sleep(3)
                        speed += 1
                        await callback_query.message.answer(
                            f'<b>Серия:</b> \n{hlink(seria[0], seria[1])}\n'
                            f'<b>Дата выхода серии:</b> \n{seria[2]}\n'
                            f'<b>Вышедшие озвучки:</b> \n{", ".join(seria[3])}\n',
                            disable_web_page_preview=True)
        elif date in ["4", "5"]:
            await state.set_state(Form_date.publish_date)
            if date == "4":
                await callback_query.message.answer(
                    "Введи количество дней, за которое хочешь узнать информацию о сериалах"
                    "(Например, чтобы получить информацию о сериалах за 5 дней, введи: 5)")
            else:
                await callback_query.message.answer(
                    "Введи дату, начиная с которой ты хочешь узнать информацию о сериалах"
                    "(Например, чтобы получить информацию о сериалах с 30 сентября 2021 года, введи: 30-09-2021)")
    except Exception as e:
        print(e)


# Сюда приходит ответ с сериалами и обрабатывается
@dp.message(Form_date.publish_date)
async def save_add_serials(message: types.Message, state: FSMContext):
    try:
        publish_date = message.text
        if publish_date.isdigit():
            if int(publish_date) < 366 and int(publish_date) >= 0:
                await message.reply("Подождите, собирается информация...")
                serials = user_news(message.from_user.id, f"{publish_date}")
                if len(serials) == 0:
                    await message.answer("Новинок нет")
                elif serials == "Пусто":
                    await message.answer("Вы ещё не добавили ни один фильм.")
                else:
                    dict_keys = sorted(serials.keys())
                    speed = 0
                    for i in dict_keys:
                        serial = serials.get(i)
                        await message.answer(f"<b>Сериал:\n{i}</b>")
                        for seria in serial:
                            if speed % 10 == 0:
                                await sleep(3)
                            speed += 1
                            await message.answer(
                                f'<b>Серия:</b> \n{hlink(seria[0], seria[1])}\n'
                                f'<b>Дата выхода серии:</b> \n{seria[2]}\n'
                                f'<b>Вышедшие озвучки:</b> \n{", ".join(seria[3])}\n',
                                disable_web_page_preview=True)
                await state.clear()
            else:
                await message.reply("Вы ввели некорректное число (Число должно быть в промежутке 0-365), "
                                    "попробуйте снова(или введите: 'отмена'): ")
        else:
            try:
                year_ago = datetime.today().date() - timedelta(days=365)
                if datetime.today().date() >= datetime.strptime(publish_date, '%d-%m-%Y').date() >= year_ago:
                    await message.reply("Подождите, собирается информация...")
                    serials = user_news(message.from_user.id, f"{publish_date}")
                    if len(serials) == 0:
                        await message.answer("Новинок нет")
                    elif serials == "Пусто":
                        await message.answer("Вы ещё не добавили ни один фильм.")
                    else:
                        dict_keys = sorted(serials.keys())
                        speed = 0
                        for i in dict_keys:
                            serial = serials.get(i)
                            await message.answer(f"<b>Сериал:\n{i}</b>")
                            for seria in serial:
                                if speed % 10 == 0:
                                    await sleep(3)
                                speed += 1
                                await message.answer(
                                    f'<b>Серия:</b> \n{hlink(seria[0], seria[1])}\n'
                                    f'<b>Дата выхода серии:</b> \n{seria[2]}\n'
                                    f'<b>Вышедшие озвучки:</b> \n{", ".join(seria[3])}\n',
                                    disable_web_page_preview=True)
                    await state.clear()
                else:
                    await message.reply("Вы ввели не корректную дату (Дата должна быть в формате: число-месяц-год), "
                                        "попробуйте снова(или введите: 'отмена')")
            except:
                await message.reply("Вы ввели не корректную дату (Дата должна быть в формате: число-месяц-год), "
                                    "попробуйте снова(или введите: 'отмена')")
    except Exception as e:
        print(e)


# Сбрасывает данные о пользователе
@dp.message(Command('reboot'))
async def add_serials_command(message: types.Message):
    try:
        reboot(message.from_user.id)
        await message.reply("Информация о Вас успешно сброшена.")
    except Exception as e:
        print(e)


# Управление сериалами
@dp.message(Command('my_serials'))
async def my_serials_command(msg: types.Message):
    try:
        otvet = user_info(msg.from_user.id)[1:]
        otvet.sort()
        keyboard_builder = InlineKeyboardBuilder()
        for i in otvet:
            keyboard_builder.add(types.InlineKeyboardButton(text=i, callback_data=f"serial_info {i}"))
        if len(otvet) == 0:
            await msg.reply(
                "Вы ещё не добавили сериалы для отслеживания. Чтобы добавить, введите команду: /add_serials")
        else:
            await msg.reply(
                "Ниже представлен список выбранных тобой сериалов, выбери о каком из них хочешь получить информацию.",
                reply_markup=keyboard_builder.as_markup())
    except Exception as e:
        print(e)


# Вывод информации о сериале
@dp.callback_query(lambda callback_query: callback_query.data.lower().startswith("serial_info"))
async def process_callback_button1(callback_query: types.CallbackQuery):
    try:
        serial = callback_query.data[12:].strip()
        await callback_query.answer()
        information = serial_info(serial)
        await callback_query.message.answer(
            f'<b>Информация о сериале:</b> \n{hlink(information["name"], information["url"])}\n'
            f'<b>Количество сезонов:</b> {information["num_season"]}\n'
            f'<b>Последняя серия:</b> \n{hlink(information["last_seria_name"], information["last_seria_url"])}\n'
            f'<b>Дата выхода серии:</b> \n{information["date"]}\n'
            f'<b>Вышедшие озвучки:</b> \n{", ".join(information["voices"])}\n',
            disable_web_page_preview=True)
    except Exception as e:
        print(e)


# Добавить сериалы в список для отслеживания
@dp.message(Command('add_serials'))
async def add_serials_command(message: types.Message, state: FSMContext):
    try:
        await state.set_state(Form_serial.serials)
        await state.update_data(command='addserials')
        await message.reply(
            "Введи названия сериалов через ':> ', для добавления в список отслеживания "
            "(Пример: Игра в кальмара:> Игра престолов):\nИли можешь написать 'отмена'")
    except Exception as e:
        print(e)


# Удалить сериалы из списка отслеживания
@dp.message(Command('delete_serials'))
async def delete_serials_command(message: types.Message, state: FSMContext):
    try:
        await state.set_state(Form_serial.serials)
        await state.update_data(command='deleteserials')
        await message.reply(
            "Введи названия сериалов через ':> ', для удаления (Пример: Игра в кальмара:> Игра престолов):\n"
            "Или можешь написать 'отмена'")
    except Exception as e:
        print(e)


# Сюда приходит ответ с сериалами и отбрабатывается
@dp.message(Form_serial.serials)
async def save_add_serials(message: types.Message, state: FSMContext):
    try:
        serials = message.text.strip()
        await message.reply("Подождите, сериалы проверяются...")
        data = await state.get_data()
        command = data['command']
        otvet = refactor_serials(message.from_user.id, serials, command)
        if command == "deleteserials":
            if otvet == "Ok":
                await message.answer("Сериалы были успешно удалены!")
            elif otvet == "None":
                await message.answer("Попробуйте позже, сервер не работает.")
            else:
                answer = "\n".join(otvet)
                await message.answer(
                    "Не все сериалы вышло удалить (Необходимо указывать полное имя сериала! "
                    "Список ваших сериалов можно посмотреть тут: /my_serials)\n"
                    f"Список сериалов, которые не вышло удалить: {answer}")
        elif command == "addserials":
            if otvet == "Ok":
                await message.answer("Сериалы были успешно добавлены!")
            else:
                answer = "\n".join(otvet)
                await message.answer(
                    "Вы указали не корректное имя сериала (Имя сериала должно точно совпадать с именем "
                    f"на сайте MySeria)\nСписок сериалов, которые не вышло добавить: {answer}")
        await state.clear()
    except Exception as e:
        print(e)


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
