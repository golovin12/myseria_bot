import re
from datetime import datetime, timedelta
from time import sleep

import redis
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()
db = redis.Redis(db=1)

date_spisok = ["last_week", "last_month", "last_3month", "last_year", "last_day", "date", "my"]


# Функция для добавления и удаления сериалов
def refactor_serials(user_id, serials, func):
    try:
        print(user_id)
        serials = serials.split(":> ")

        if str(user_id) not in db:
            # Формат сохранения в базе данных: "date pplflfltt serial1 pplflfltt serial2 pplflfltt serial3"
            db[f"{user_id}"] = f"{datetime.today().date()}"

        if func == "addserials":
            user_db = db.get(f"{user_id}").decode("utf-8").split(" pplflfltt ")
            proverka = proverka_serials(serials)

            if len(proverka[1]) == 0:
                for i in proverka[0]:
                    if i in user_db:
                        proverka[0].remove(i)
                user_db = user_db + proverka[0]
                db[f"{user_id}"] = " pplflfltt ".join(user_db).lower()
                return "Ok"
            else:
                if len(proverka[0]) != 0:
                    for i in proverka[0]:
                        if i in user_db:
                            proverka[0].remove(i)
                    user_db = user_db + proverka[0]
                    db[f"{user_id}"] = " pplflfltt ".join(user_db).lower()
                return proverka[1]

        elif func == "deleteserials":
            user_db = db.get(f"{user_id}").decode("utf-8").split(" pplflfltt ")
            otvet = []
            for serial in serials:
                if serial.lower() in user_db and serial.lower() != user_db[0]:
                    user_db.remove(serial.lower())
                else:
                    otvet.append(serial.lower())

            db[f"{user_id}"] = " pplflfltt ".join(user_db).lower()
            if len(otvet) == 0:
                return "Ok"
            else:
                return otvet
    except Exception as e:
        print(e)
        return "None"


# Проверяет сколько сериалов существует с таким названием
def proverka_serials(serials):
    try:
        host = find_site_addr()
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
def serial_info(serial, date=None):
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
def user_news(user_id, date):
    try:
        user_db = db.get(f"{user_id}").decode("utf-8").split(" pplflfltt ")
        date_db = user_db[0]
        serials_db = user_db[1:]
        if len(serials_db) == 0:
            return "Пусто"
        start_date = datetime.today().date()

        if date in date_spisok[:4] or date in date_spisok[-1]:
            if date == date_spisok[0]:
                last_date = timedelta(days=7)
            elif date == date_spisok[1]:
                last_date = timedelta(days=31)
            elif date == date_spisok[2]:
                last_date = timedelta(days=93)
            elif date == date_spisok[3]:
                last_date = timedelta(days=365)
            else:
                last_date = start_date - datetime.strptime(date_db, '%Y-%m-%d').date()
                add_date(user_id, datetime.today().date())
        elif date.isdigit():
            last_date = timedelta(days=int(date))
        else:
            last_date = start_date - datetime.strptime(date, '%d-%m-%d%Y').date()

        result_date = start_date - last_date

        host = find_site_addr()
        if not host:
            print("Сайт не доступен")
            return "Пусто"
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
                            if result_date <= datetime.strptime(s, '%Y-%m-%d').date():
                                for name_n in page_serials:
                                    name = name_n.find('div', class_="field-title").find('a').text[:-5].lower()
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

            return (result)
    except Exception as e:
        print(e)
        return "Пусто"


# Позволяет задать дату отслеживания для сериалов
def add_date(user_id, date):
    user_db = db.get(f"{user_id}").decode("utf-8").split(" pplflfltt ")
    user_db[0] = date
    db[f"{user_id}"] = user_db


# Функция, сбрасывающая список отслеживаемых сериалов
def reboot(user_id):
    db[f"{user_id}"] = f"{datetime.today().date()}"


def user_info(user_id):
    vihod = db.get(f"{user_id}").decode("utf-8").split(" pplflfltt ")
    return vihod


def force_update_address(address):
    address = address.strip()
    if _address_is_correct(address):
        db["my_seria_addr"] = address
        return True
    return False


def _address_is_correct(address: str):
    if not re.fullmatch(r"^https?:.+", address):
        return False
    req_site = requests.get(address)
    if req_site.status_code == 200:
        soup_site = BeautifulSoup(req_site.text, 'lxml')
        proverka_title = str(soup_site.find("head").find("title")).lower()
        if "myseria" in proverka_title or "сериалы" in proverka_title:
            return True
    return False


# Обновление адреса сайта (адрес берется со страницы ВК)
def find_site_addr():
    vk_search_is_work = False
    if "my_seria_addr" not in db:
        db["my_seria_addr"] = ""
    address = db.get("my_seria_addr").decode('utf-8')
    if _address_is_correct(address):
        return address
    if vk_search_is_work:
        # Код ниже не работает, т.к. убрали нужную инфу из meta(
        url_vk = 'https://vk.com/myserianet'
        req_vk = requests.get(url_vk, headers={'user-agent': f"{ua.random}"})
        soup_vk = BeautifulSoup(req_vk.text, 'lxml')
        address = soup_vk.find('meta', property="og:description").get('content').split()[2]
        if _address_is_correct(address):
            db["my_seria_addr"] = address
            return address
    return False

# db = redis.Redis(db=8)
# # db["my_seria_addr"] = "http://myseria.net"
# # find_site_addr()
# for i in db.keys():
#     print(i)


# url = 'http://myseria.net/'
# r = requests.get(url)
# soup_site = BeautifulSoup(r.text, 'lxml')
# proverka_title = soup_site.find("head").find("title")
# print(proverka_title)
# s = "Флэш"
# story = "Флэш"
# url = f'http://myseria.pro/?do=search&subaction=search&story={story}'
# responce = requests.get(url=url)
# soup = BeautifulSoup(responce.text, "lxml")
# result = soup.find_all('div', class_='item-search-serial')
# print(result[0].find('div', class_='item-search-header').find('a').text)

# url = 'http://myseria.pro/series/page/2/'
# r = requests.get(url)
# with codecs.open("my_serial_seria.html", "w", "utf-8") as file:
#     file.write(r.text)

# try:
#     date = "9-9-1999"
#     valid_date = datetime.strptime(date, '%d-%m-%Y')
# except ValueError:
#     print('Invalid date!')
