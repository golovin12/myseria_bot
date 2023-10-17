import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from time import sleep
from typing import AsyncIterable

import aiohttp
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


@dataclass
class Seria:
    name: str
    url: str
    release_date: str
    voices: list[str]


@dataclass
class Serial:
    name: str
    url: str
    last_season: str
    last_seria: Seria


class ExternalService:
    user_agent: UserAgent

    @staticmethod
    async def get_site_addr() -> str:
        """Получить адрес сайта"""
        ...

    async def exist(self, serial_name: str) -> bool:
        """Проверяет, есть ли сериал с таким названием"""
        ...

    async def get_new_series_from_date(self, serial_name: str, search_date: datetime) -> AsyncIterable[Seria]:
        """Получить список новых серий у сериала с выбранной конкретной даты"""
        yield ...

    async def get_serial_info(self, serial_name: str) -> [Serial | None]:
        """Получить информацию о сериале"""
        ...


class MySeriaService(ExternalService):
    def __init__(self):
        self.headers = {'user-agent': self.user_agent.random}

    async def exist(self, serial_name: str) -> bool:
        async with aiohttp.ClientSession() as session:
            page_data = await self._find_serial_on_site(session, serial_name)
        if self._find_serial_by_page_data(page_data, serial_name):
            return True
        return False

    async def get_serial_info(self, serial_name: str) -> [Serial | None]:
        async with aiohttp.ClientSession() as session:
            page_data = await self._find_serial_on_site(session, serial_name)
            serial_data = self._find_serial_by_page_data(page_data, serial_name)
            if serial_url := serial_data.get('url'):
                # Получение недостающей информации о сериале
                async with session.get(url=serial_url, headers=self.headers) as response:
                    page_data = await response.text()
                additional_data = self._get_serial_info_by_serial_page(page_data)
                last_seria_url = additional_data.get('last_seria_url')
                if last_seria_url:
                    # Получение информации о последней серии
                    async with session.get(url=last_seria_url, headers=self.headers) as response:
                        page_data = await response.text()
                    if last_seria := self._get_seria_by_seria_page(page_data, last_seria_url):
                        return Serial(name=serial_data['name'],
                                      url=serial_url,
                                      last_season=additional_data.get('last_season', '-'),
                                      last_seria=last_seria
                                      )
        return None

    async def get_new_series_from_date(self, serial_name: str, search_date: datetime) -> AsyncIterable[Seria]:
        serial = []  # todo
        for seria in serial:
            yield seria

    async def _find_serial_on_site(self, session: aiohttp.ClientSession, serial_name: str) -> str:
        serial_search_name = re.sub(' ', '+', serial_name)
        host = await self.get_site_addr()
        url = f'{host}/?do=search&subaction=search&story={serial_search_name}'
        async with session.get(url=url, headers=self.headers) as response:
            page_data = await response.text()
        return page_data

    @staticmethod
    def _find_serial_by_page_data(page_data: str, serial_name: str) -> dict:
        """Проверяет, есть ли нужный сериал среди найденных"""
        serial_name = serial_name.lower()
        soup = BeautifulSoup(page_data, "lxml")
        found_serials = soup.find_all('div', class_='item-search-serial')
        for serial_block in found_serials:
            if serial_header := serial_block.find('div', class_='item-search-header'):
                if serial_link := serial_header.find('a'):
                    found_serial_name = serial_link.text
                    if found_serial_name.lower() == serial_name:
                        return {'name': found_serial_name, 'url': serial_link.get('href')}
        return {}

    def _get_serial_info_by_serial_page(self, page_data: str) -> dict:
        result = {}
        soup = BeautifulSoup(page_data, 'lxml')
        if last_season_header := soup.find('div', class_="episode-group-name"):
            if las_season_span := last_season_header.find("span"):
                result["last_season"] = las_season_span.text
        if last_seria_block := soup.find('div', class_="item-serial"):
            if last_seria_title := last_seria_block.find("div", class_="field-title"):
                if last_seria_link := last_seria_title.find("a"):
                    if last_seria_url := last_seria_link.get("href"):
                        result['last_seria_url'] = last_seria_url
        return result

    def _get_seria_by_seria_page(self, page_data: str, last_seria_url: str) -> [Seria | None]:
        """Получение инфо о серии со страницы серии"""
        seria_name = None
        seria_release = "Нет информации"
        seria_voices = []
        soup = BeautifulSoup(page_data, 'lxml')
        if seria_title_block := soup.find("div", class_="title-links-wrapper clearfix"):
            if seria_title := seria_title_block.find('h1', class_='page-title'):
                seria_name = seria_title.text
        if seria_description_block := soup.find("div", class_="serial-box-description-torrent"):
            if release_description := seria_description_block.find("div", class_="date-time-description"):
                seria_release = release_description.text
        if voices_block := soup.find("div", class_="sounds-wrapper"):
            if voices_list := voices_block.find("div", class_="sounds-list"):
                seria_voices = [voice.text for voice in voices_list.find_all("div")]
        if seria_name is None:
            return None
        return Seria(
            name=seria_name,
            url=last_seria_url,
            release_date=seria_release,
            voices=seria_voices,
        )


mounth = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
          "декабря"]


# Выводит информацию об отслеживаемых сериалах
def user_news(user_id, date=None):
    # todo сделать более отказоустойчивым. Заменить на асинхронные запросы в сеть
    try:
        serials_db = ['импульс мира']
        end_date = (datetime.today() - timedelta(days=1)).date()

        host = "https://serialrun.ru"
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
