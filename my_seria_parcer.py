import asyncio
import json
import re
from datetime import datetime, timedelta
from time import sleep

import redis
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()
aioredis = redis.asyncio.Redis(db=1)
redis_client = redis.Redis(db=1)

"""Хранилище:
{user_id: {serial1: last_search_date,
           serial2: last_search_date
           }}
"""


# todo вынести работу с aioredis в отдельный блок
async def create_user_if_not_exist(user_id: int) -> bool:
    return await aioredis.setnx(f"{user_id}_serials", "{}")


async def get_user_serials(user_id: int) -> dict:
    user_serials = await aioredis.get(f"{user_id}_serials")
    if user_serials:
        return json.loads(user_serials)
    return {}


async def set_user_serials(user_id: int, serials: dict) -> bool:
    return await aioredis.set(f"{user_id}_serials", json.dumps(serials))


async def get_new_series_by_date(serial_name: str, last_search_date: str):
    # todo искать новые серии на сайте MySerial и возвращать инфо о них
    try:
        for i in range(3):
            await asyncio.sleep(3)
            yield f"seria{i}"
    except:
        yield f'При попытке получения информации о сериале "{serial_name}" произошла ошибка, попробуйте ещё раз.'


async def get_user_new_series(user_id: int, search: str):
    user_serials = await get_user_serials(user_id)
    if search != '__all__':
        if search not in user_serials:
            yield f'Сериал "{search}" не найден в списке отслеживаемых.'
            return
        user_serials = {search: user_serials[search]}

    is_have_update = False
    for serial_name, last_search_date in user_serials.items():
        async for seria_data in get_new_series_by_date(serial_name, last_search_date):
            is_have_update = True
            yield seria_data
    if not is_have_update:
        yield 'Новые серии не найдены.'


async def user_add_serial(user_id: int, serial: str) -> str:
    # todo добавить проверку наличия сериала на сайте MySerial
    user_serials = await get_user_serials(user_id)
    user_serials[serial] = datetime.now().strftime('%d.%m.%Y %H:%M')
    result = await set_user_serials(user_id, user_serials)
    if result:
        return f"Сериал {serial} был успешно добавлен!\nМожете указать название другого сериала для добавления."
    return f"Не удалось добавить сериал {serial}, попробуйте ещё раз."
    return ("Вы указали не корректное имя сериала (Имя сериала должно точно совпадать с именем на сайте MySeria)\n"
            f"Сериал, который не вышло добавить: {serial}")


async def user_delete_serial(user_id: int, serial: str) -> tuple[str, bool]:
    user_serials = await get_user_serials(user_id)
    if serial in user_serials:
        del user_serials[serial]
        result = await set_user_serials(user_id, user_serials)
        if result:
            return f"Сериал {serial} был успешно удален!\nМожете выбрать ещё сериал для удаления.", True
        return f"Не удалось удалить сериал {serial}, попробуйте ещё раз.", False
    return f"Не удалось удалить сериал {serial}, т.к. он не найден в списке отслеживаемых сериалов", False


async def force_update_address(address):
    # todo использовать асинхронный запрос в сеть
    address = address.strip()
    req_site = requests.get(address)
    if req_site.status_code == 200:
        await aioredis.set("my_seria_url", address)
        return True
    return False


def get_site_addr():
    url: bytes = redis_client.get("my_seria_url")
    if url:
        return url.decode('utf-8')
    return 'https://'


# Проверяет сколько сериалов существует с таким названием
def proverka_serials(serials):
    # todo сделать более отказоустойчивым. Заменить на асинхронные запросы в сеть
    try:
        host = get_site_addr()
        user_ag = ua.random
        otvet = [[], [], []]
        with requests.Session() as sess:
            for serial in serials:
                s = serial.split()
                story = "+".join(s)
                url = f'{host}/?do=search&subaction=search&story={story}'
                responce = sess.get(url=url, headers={'user-agent': f"{user_ag}"})
                soup = BeautifulSoup(responce.text, "lxml")
                result = soup.find_all('div', class_='item-search-serial')
                if len(result) == 1:
                    if result[0].find('div', class_='item-search-header').find('a').text.lower() == serial.lower():
                        otvet[0].append(serial)
                        otvet[2] = result[0].find('div', class_='item-search-header').find('a').get('href')
                    else:
                        otvet[1].append(serial)
                elif len(result) == 0:
                    otvet[1].append(serial)
                elif len(result) > 1:
                    c = 0
                    for item in result:
                        if item.find('div', class_='item-search-header').find('a').text.lower() == serial.lower():
                            c = 1
                            break
                    if c == 1:
                        otvet[0].append(serial)
                        otvet[2] = result[0].find('div', class_='item-search-header').find('a').get('href')
                    else:
                        otvet[1].append(serial)
        return otvet
    except Exception as e:
        print(e)
        return [[], serials, []]


# Выводит информацию о выбранном сериале
def get_serial_info(serial, date=None):
    # todo сделать более отказоустойчивым. Заменить на асинхронные запросы в сеть
    informations = {}
    serial_link = proverka_serials([serial])[2]
    informations["name"] = serial
    informations["url"] = serial_link
    url_serial = serial_link
    req_serial = requests.get(url_serial)
    soup_serial = BeautifulSoup(req_serial.text, 'lxml')
    informations["num_season"] = soup_serial.find('div', class_="episode-group-name").find("span").text
    last_seria_link = soup_serial.find('div', class_="page-content").find("div", class_="item-serial").find("div",
                                                                                                            class_="field-title").find(
        "a").get("href")
    informations["last_seria_url"] = last_seria_link
    req_seria = requests.get(last_seria_link)
    soup_seria = BeautifulSoup(req_seria.text, 'lxml')
    informations["last_seria_name"] = soup_seria.find("div", class_="title-links-wrapper clearfix").find("div",
                                                                                                         class_="gap-correct").find(
        'h1').text
    date = soup_seria.find("div", class_="serial-box-description-torrent")
    if date is None:
        date = "Нет информации"
    else:
        date = date.find("div", class_="date-time-description").text
    informations["date"] = date
    voices = soup_seria.find("div", class_="sounds-wrapper").find("div", class_="sounds-list").find_all("div")
    voi_vih = []
    for i in voices:
        voi_vih.append(i.text)
    informations["voices"] = voi_vih
    return informations


mounth = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
          "декабря"]


# Выводит информацию об отслеживаемых сериалах
def user_news(user_id, date=None):
    # todo сделать более отказоустойчивым. Заменить на асинхронные запросы в сеть
    try:
        serials_db = ['импульс мира']
        end_date = (datetime.today() - timedelta(days=1)).date()

        host = get_site_addr()
        if not host:
            print("Сайт не доступен")
            return "Сайт не доступен"
        with requests.Session() as sess:
            page = 1
            result = {}
            while True:
                url = f'{host}/series/page/{page}/'
                req = sess.get(url)
                soup_serials = BeautifulSoup(req.text, 'lxml')
                page_dates = soup_serials.find('div', class_="page-content").find_all('div', class_="episode-group")
                t = 0
                for s_date in page_dates:
                    s = s_date.find('div', class_="episode-group-name").find("span").text
                    page_serials = s_date.find_all('div', class_="item")
                    if t != 0:
                        break
                    not_read = 0
                    for index, m in enumerate(mounth, start=1):
                        if t != 0:
                            break
                        if m in s:
                            s = s.split(f" {m} ")
                            s = f"{s[1]}-{index}-{s[0]}"
                            if end_date <= datetime.strptime(s, '%Y-%m-%d').date():
                                for name_n in page_serials:
                                    name = name_n.find('div', class_="field-title").find('a').text[:-5].lower()
                                    print(name)
                                    if name in serials_db:
                                        spis = []
                                        if name in result:
                                            spis = result.get(name)
                                        spis.append(
                                            [name + " " + name_n.find('div', class_="field-description").find('a').text,
                                             name_n.find('div', class_="field-title").find('a').get("href"), s,
                                             [i.find('a').text for i in
                                              name_n.find('div', class_="serial-translate").find_all('span')]])
                                        result[name] = spis
                            else:
                                t += 1
                        else:
                            not_read += 1
                    if not_read == 12:
                        print(f"Ошибка чтения даты: {s}")
                if t != 0:
                    break

                if page % 5 == 0:
                    sleep(3)
                page += 1
            print(result)
            return result
    except Exception as e:
        print(e)
        return "Вы ещё не добавили ни один фильм."
