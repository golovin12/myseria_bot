import asyncio
import json
import re
from datetime import datetime, timedelta
from time import sleep

import aiohttp
import redis
import requests
from aiogram.utils.markdown import hlink
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from consts import MY_SERIA_KEY

ua = UserAgent()
redis_client = redis.Redis(db=1)


def get_site_addr():
    url: bytes = redis_client.get(MY_SERIA_KEY)
    if url:
        return url.decode('utf-8')
    return 'https://'


class ExternalService:
    async def exist(self, serial: str) -> bool:
        # todo serial = serial.lower()
        ...

    async def get_new_series_from_date(self, serial_name: str, search_date: datetime) -> AsyncIterable[Seria]:
        # todo
        yield ...


class MySeriaService(ExternalService):
    ...


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
async def get_serial_info(serial: str) -> str:
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
    info = informations
    return (f'<b>Информация о сериале:</b> \n{hlink(info["name"], info["url"])}\n'
           f'<b>Количество сезонов:</b> {info["num_season"]}\n'
           f'<b>Последняя серия:</b> \n{hlink(info["last_seria_name"], info["last_seria_url"])}\n'
           f'<b>Дата выхода серии:</b> \n{info["date"]}\n'
           f'<b>Вышедшие озвучки:</b> \n{", ".join(info["voices"])}\n')


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
