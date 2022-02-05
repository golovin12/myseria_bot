import aiogram.utils.markdown as md
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.markdown import hlink, hbold
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from asyncio import sleep
from my_seria_parcer import refactor_serials, user_info, serial_info, user_news, reboot
from datetime import datetime, timedelta
from token_bot import token_bot

TOKEN = token_bot.TOKEN
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2('localhost', 6379, db=5, pool_size=10, prefix='my_fsm_key')
dp = Dispatcher(bot, storage=storage)
date_spisok = ["last_week", "last_month", "last_3month", "last_year", "last_day", "date", "my"]
date_spisok2 = ["Последняя неделя", "Последний месяц", "Последние 3 месяца", "Последний год", "Последние N дней", "Своя дата", "Последний запрос"]


# создаём форму и указываем поля
class Form_serial(StatesGroup):
    serials = State()
    command = State()

class Form_date(StatesGroup):
    publish_date = State()

# Приветствие
@dp.message_handler(commands=['start'])
async def start_command(msg: types.Message):
    try:
        refactor_serials(msg.from_user.id, "", None)
        command_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        add_ser = types.KeyboardButton('/add_serials')
        my_ser = types.KeyboardButton('/my_serials')
        del_ser = types.KeyboardButton('/delete_serials')
        ser_news = types.KeyboardButton('/serials_news')
        help_b = types.KeyboardButton('/help')
        command_keyboard.row(add_ser, my_ser)
        command_keyboard.row(del_ser, ser_news)
        command_keyboard.row(help_b)
        await msg.reply("Привет, данный бот предназначен для отслеживания выхода серий с сайта MySeria.\n"
                         "Вы можете ввести названия сериалов, которые бот будет отслеживать.\n"
                         "Для каждого сериала можете выбрать число, с которого нужно отслеживать выход серий.\n"
                         "Также данный бот может показать вышедшие озвучки для конкретной серии.\n"
                         "Для того, чтобы добавить сериалы в список для отслеживания, введите команду: /add_serials\n"
                         "Для того, чтобы удалить сериалы из списка для отслеживания, введите команду: /delete_serials\n"
                         "Для того, чтобы получить информацию по сериалам, введите команду: /my_serials\n"
                         "Для того, чтобы узнать о выходе новых серий, введите команду: /serials_news\n"
                         "Для того, чтобы обнулить список сериалов для отслеживания, введите команду: /reboot\n"
                         "Для того, чтобы увидеть список возможных команд, введите команду: /help\n", reply_markup=command_keyboard)
    except Exception as e:
        print(e)

# Список возможных команд
@dp.message_handler(commands=['help'])
async def start_command(msg: types.Message):
    try:
        await msg.reply("Список доступных команд:\n"
                        "/start - Приветствие\n"
                        "/help - Список команд\n"
                        "/add_serials - Добавить сериалы для отслеживания\n"
                        "/delete_serials - Убрать сериалы из отслеживания\n"
                        "/my_serials - Получение информации по отдельным сериалам\n"
                        "/serials_news - Получить информацию о вышедших сериалах за последнее время\n"
                        "/reboot - Сбросить весь список сериалов\n")
    except Exception as e:
        print(e)

# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        if current_state is None:
            return

        await state.finish()
        await message.reply('ОК')
    except Exception as e:
        print(e)

# Выводит информацию о последних сериях
@dp.message_handler(commands=['serials_news'])
async def add_serials_command(message: types.Message):
    try:
        serials_keyboard = types.InlineKeyboardMarkup()
        for i in range(len(date_spisok)):
            serials_keyboard.add(types.InlineKeyboardButton(date_spisok2[i], callback_data=f"serial_news {i}"))
        await message.reply("Выберите, за какую дату вы хотите получить информацию:", reply_markup=serials_keyboard)
    except Exception as e:
        print(e)

@dp.callback_query_handler(Text(startswith="serial_news", ignore_case=True))
async def process_callback_button1(callback_query: types.CallbackQuery):
    try:
        date = callback_query.data[12:]
        if date in ["0", "1", "2", "3", "6"]:
            await bot.send_message(callback_query.from_user.id, "Подождите, собирается информация...")
            await bot.answer_callback_query(callback_query.id)
            serials = user_news(callback_query.from_user.id, date_spisok[int(date)])
            if len(serials) == 0:
                await bot.send_message(callback_query.from_user.id, "Новинок нет.")
            elif serials == "Пусто":
                await bot.send_message(callback_query.from_user.id, "Вы ещё не добавили ни один фильм.")
            else:
                dict_keys = sorted(serials.keys())
                speed = 0
                for i in dict_keys:
                    serial = serials.get(i)
                    await bot.send_message(callback_query.from_user.id, f"<b>Сериал:\n{i}</b>")
                    for seria in serial:
                        if speed%10 == 0:
                            await sleep(3)
                        speed += 1
                        await bot.send_message(callback_query.from_user.id,
                                       f'<b>Серия:</b> \n{hlink(seria[0], seria[1])}\n'
                                       f'<b>Дата выхода серии:</b> \n{seria[2]}\n'
                                       f'<b>Вышедшие озвучки:</b> \n{", ".join(seria[3])}\n',
                                       disable_web_page_preview=True)
        elif date in ["4", "5"]:
            await Form_date.publish_date.set()
            if date == "4":
                await bot.send_message(callback_query.from_user.id,
                                       "Введи количество дней, за которое хочешь узнать информацию о сериалах"
                                       "(Например, чтобы получить информацию о сериалах за 5 дней, введи: 5)")
            else:
                await bot.send_message(callback_query.from_user.id,
                                       "Введи дату, начиная с которой ты хочешь узнать информацию о сериалах"
                                       "(Например, чтобы получить информацию о сериалах с 30 сентября 2021 года, введи: 30-09-2021)")
    except Exception as e:
        print(e)

# Сюда приходит ответ с сериалами и отбрабатывается
@dp.message_handler(state=Form_date.publish_date)
async def save_add_serials(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['publish_date'] = message.text
        if data['publish_date'].isdigit():
            if int(data['publish_date']) < 366 and int(data['publish_date']) >= 0:
                await message.reply("Подождите, собирается информация...")
                serials = user_news(message.from_user.id, f"{data['publish_date']}")
                if len(serials) == 0:
                    await bot.send_message(message.from_user.id, "Новинок нет")
                elif serials == "Пусто":
                    await bot.send_message(message.from_user.id, "Вы ещё не добавили ни один фильм.")
                else:
                    dict_keys = sorted(serials.keys())
                    speed = 0
                    for i in dict_keys:
                        serial = serials.get(i)
                        await bot.send_message(message.from_user.id, f"<b>Сериал:\n{i}</b>")
                        for seria in serial:
                            if speed % 10 == 0:
                                await sleep(3)
                            speed += 1
                            await bot.send_message(message.from_user.id,
                                                   f'<b>Серия:</b> \n{hlink(seria[0], seria[1])}\n'
                                                   f'<b>Дата выхода серии:</b> \n{seria[2]}\n'
                                                   f'<b>Вышедшие озвучки:</b> \n{", ".join(seria[3])}\n',
                                                   disable_web_page_preview=True)
                await state.finish()
            else:
                await message.reply("Вы ввели некорректное число (Число должно быть в промежутке 0-365), попробуйте снова(или введите: 'отмена'): ")

        else:
            try:
                if datetime.strptime(data['publish_date'], '%d-%m-%Y').date() <= datetime.today().date() and datetime.strptime(data['publish_date'], '%d-%m-%Y').date() >= (datetime.today().date()-timedelta(days=365)):
                    await message.reply("Подождите, собирается информация...")
                    serials = user_news(message.from_user.id, f"{data['publish_date']}")
                    if len(serials) == 0:
                        await bot.send_message(message.from_user.id, "Новинок нет")
                    elif serials == "Пусто":
                        await bot.send_message(message.from_user.id, "Вы ещё не добавили ни один фильм.")
                    else:
                        dict_keys = sorted(serials.keys())
                        speed = 0
                        for i in dict_keys:
                            serial = serials.get(i)
                            await bot.send_message(message.from_user.id, f"<b>Сериал:\n{i}</b>")
                            for seria in serial:
                                if speed % 10 == 0:
                                    await sleep(3)
                                speed += 1
                                await bot.send_message(message.from_user.id,
                                                       f'<b>Серия:</b> \n{hlink(seria[0], seria[1])}\n'
                                                       f'<b>Дата выхода серии:</b> \n{seria[2]}\n'
                                                       f'<b>Вышедшие озвучки:</b> \n{", ".join(seria[3])}\n',
                                                       disable_web_page_preview=True)
                    await state.finish()
                else:
                    await message.reply(
                        "Вы ввели не корректную дату (Дата должна быть в формате: число-месяц-год), попробуйте снова(или введите: 'отмена')")
            except:
                await message.reply("Вы ввели не корректную дату (Дата должна быть в формате: число-месяц-год), попробуйте снова(или введите: 'отмена')")
    except Exception as e:
        print(e)

# Сбрасывает данные о пользователе
@dp.message_handler(commands=['reboot'])
async def add_serials_command(message: types.Message):
    try:
        reboot(message.from_user.id)
        await message.reply("Информация о Вас успешно сброшена.")
    except Exception as e:
        print(e)

# Управление сериалами
@dp.message_handler(commands=['my_serials'])
async def my_serials_command(msg: types.Message):
    try:
        serials_keyboard = types.InlineKeyboardMarkup()
        otvet = user_info(msg.from_user.id)[1:]
        otvet.sort()
        for i in otvet:
            serials_keyboard.add(types.InlineKeyboardButton(i, callback_data=f"serial_info {i}"))
        if len(otvet) == 0:
            await msg.reply("Вы ещё не добавили сериалы для отслеживания. Чтобы добавить, введите команду: /add_serials")
        else:
            await msg.reply("Ниже представлен список выбранных тобой сериалов, выбери о каком из них хочешь получить информацию.", reply_markup=serials_keyboard)
    except Exception as e:
        print(e)

# Вывод информации о сериале
@dp.callback_query_handler(Text(startswith="serial_info", ignore_case=True))
async def process_callback_button1(callback_query: types.CallbackQuery):
    try:
        serial = callback_query.data[12:]
        await bot.answer_callback_query(callback_query.id)
        informations = serial_info(serial)
        await bot.send_message(callback_query.from_user.id, f'<b>Информация о сериале:</b> \n{hlink(informations["name"], informations["url"])}\n'
                                                            f'<b>Количество сезонов:</b> {informations["num_season"]}\n'
                                                            f'<b>Последняя серия:</b> \n{hlink(informations["last_seria_name"], informations["last_seria_url"])}\n'
                                                            f'<b>Дата выхода серии:</b> \n{informations["date"]}\n'
                                                            f'<b>Вышедшие озвучки:</b> \n{", ".join(informations["voices"])}\n', disable_web_page_preview=True)
    except Exception as e:
        print(e)

# Добавить сериалы в список для отслеживания
@dp.message_handler(commands=['add_serials'])
async def add_serials_command(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['command'] = "addserials"
        await Form_serial.serials.set()
        await message.reply("Введи названия сериалов через ':> ', для добавления в список отслеживания(Пример: Игра в кальмара:> Игра престолов):\n"
                            "Или можешь написать 'отмена'")
    except Exception as e:
        print(e)

# Удалить сериалы из списка отслеживания
@dp.message_handler(commands=['delete_serials'])
async def delete_serials_command(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['command'] = "deleteserials"
        await Form_serial.serials.set()
        await message.reply("Введи названия сериалов через ':> ', для удаления(Пример: Игра в кальмара:> Игра престолов):\n"
                            "Или можешь написать 'отмена'")
    except Exception as e:
        print(e)

# Сюда приходит ответ с сериалами и отбрабатывается
@dp.message_handler(state=Form_serial.serials)
async def save_add_serials(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['serials'] = message.text
        await message.reply("Подождите, сериалы проверяются...")
        otvet = refactor_serials(message.from_user.id, data['serials'], data['command'])
        if data['command'] == "deleteserials":
            if otvet == "Ok":
                await message.answer("Сериалы были успешно удалены!")
            elif otvet == "None":
                await message.answer("Попробуйте позже, сервер не работает.")
            else:
                answer = "\n".join(otvet)
                await message.answer(
                    f"Не все сериалы вышло удалить (Необходимо указывать полное имя сериала! Список ваших сериалов можно посмотреть тут: /my_serials)\n"
                    f"Список сериалов, которые не вышло удалить: {answer}")
        elif data['command'] == "addserials":
            if otvet == "Ok":
                await message.answer("Сериалы были успешно добавлены!")
            else:
                answer = "\n".join(otvet)
                await message.answer(f"Вы указали не корректное имя сериала (Имя сериала должно точно совпадать с именем на сайте MySeria)\n"
                                     f"Список сериалов, которые не вышло добавить: {answer}")
        await state.finish()
    except Exception as e:
        print(e)


async def shutdown(dp: Dispatcher):
    try:
        await dp.storage.close()
        await dp.storage.wait_closed()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
