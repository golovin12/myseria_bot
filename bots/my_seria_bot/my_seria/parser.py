import asyncio
import re
from datetime import datetime
from typing import AsyncIterator, Iterator

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from consts import MY_SERIA
from database.models import SerialSite
from utils import get_date_by_localize_date_string, url_is_active
from .serials import FindSerialsHelper, Serial, Seria


# todo отделить логику парсинга и запросы в сеть

class MySeriaService:
    _user_agent_class = UserAgent

    def __init__(self):
        self.headers = {'user-agent': self._user_agent_class().random}

    async def exist(self, serial_name: str) -> bool:
        """Проверяет, есть ли сериал с таким названием"""
        async with aiohttp.ClientSession() as session:
            page_data = await self._find_serial_on_site(session, serial_name)
        if self._find_serial_by_search_page(page_data, serial_name):
            return True
        return False

    async def get_serial_info(self, serial_name: str) -> Serial | None:
        """Получить информацию о сериале"""
        serial_name = serial_name.strip()
        async with aiohttp.ClientSession() as session:
            page_data = await self._find_serial_on_site(session, serial_name)
            serial_data = self._find_serial_by_search_page(page_data, serial_name)
            if serial_data is None:
                return None
            serial_url = serial_data['url']
            # Получение недостающей информации о сериале
            async with session.get(url=serial_url, headers=self.headers) as response:
                serial_page_data = await response.text()
            additional_data = self._get_serial_info_by_serial_page(serial_page_data)
            last_seria_url = additional_data['last_seria_url']
            # Получение информации о последней серии
            async with session.get(url=last_seria_url, headers=self.headers) as response:
                seria_page_data = await response.text()
        last_seria = self._get_seria_by_seria_page(seria_page_data)
        last_seria.url = last_seria_url
        return Serial(name=serial_data['name'],
                      url=serial_url,
                      last_season=additional_data['last_season'],
                      last_seria=last_seria
                      )

    async def get_new_series(self, find_serials_helper: FindSerialsHelper) -> AsyncIterator[Seria]:
        """Получить информацию о новых сериях"""
        # 2 точки выхода: 1) превышен лимит в 120 страниц; 2) все сериалы были просмотрены (StopIteration)
        try:
            host = await self._get_my_seria_url()
            page = 1
            last_date_iterator = find_serials_helper.get_date_and_update_serials()
            last_date = next(last_date_iterator)
            semaphore = asyncio.Semaphore(5)
            async with aiohttp.ClientSession() as session:
                while page < 120:
                    async with semaphore:
                        page_url = f'{host}/series/page/{page}/'
                        async with session.get(url=page_url, headers=self.headers) as response:
                            page_data = await response.text()
                        soup = BeautifulSoup(page_data, 'lxml')
                        series_by_dates = soup.find_all('div', class_="episode-group")
                        for series_block in series_by_dates:
                            series_date = self._get_date_from_series_block(series_block)
                            if last_date > series_date:
                                last_date = next(last_date_iterator)
                            for seria in self._get_series_by_series_block(series_block):
                                if seria.name.capitalize() in find_serials_helper.unupdated_serials:
                                    seria.release_date = series_date.strftime("%d.%m.%Y")
                                    yield seria
                    page += 1
        except StopIteration:
            pass

    async def _find_serial_on_site(self, session: aiohttp.ClientSession, serial_name: str) -> str:
        """Поисковый запрос на поиск сериала"""
        # todo информирование, если изменилась структура запроса / сайт не работает
        serial_search_name = re.sub(' ', '+', serial_name)
        host = await self._get_my_seria_url()
        url = f'{host}/?do=search&subaction=search&story={serial_search_name}'
        async with session.get(url=url, headers=self.headers) as response:
            page_data = await response.text()
        return page_data

    @staticmethod
    async def _get_my_seria_url() -> str:
        my_seria_site = await SerialSite.get_object(MY_SERIA)
        return my_seria_site.url

    @staticmethod
    def _get_series_by_series_block(series_block: BeautifulSoup) -> Iterator[Seria]:
        """Получить информацию о сериях из блока с сериями"""
        # todo информирование, если изменилась структура страницы
        series_items = series_block.find_all('div', class_="item")
        for seria_item in series_items:
            seria_bottom = seria_item.find('div', class_="serial-bottom")
            seria_title = seria_bottom.find('div', class_="field-title").find('a')
            seria_number = seria_bottom.find('div', class_="field-description").find('a').text
            name = re.sub(r' \d{4}$', '', seria_title.text.strip())
            url = seria_title.get("href")
            voices = [voice.text for voice in seria_item.find('div', class_="serial-translate").find_all('a')]
            yield Seria(name=name, number=seria_number, url=url, voices=voices, release_date="")

    @staticmethod
    def _get_date_from_series_block(series_block: BeautifulSoup) -> datetime:
        """Получить дату из блока с сериями"""
        # todo информирование, если изменилась структура страницы
        date_text = series_block.find('div', class_="episode-group-name").find("span").text
        return get_date_by_localize_date_string(date_text)

    @staticmethod
    def _find_serial_by_search_page(page_data: str, serial_name: str) -> dict[str, str] | None:
        """Проверяет, есть ли нужный сериал среди найденных"""
        # todo информирование, если изменилась структура страницы
        serial_name = serial_name.lower()
        soup = BeautifulSoup(page_data, "lxml")
        found_serials = soup.find_all('div', class_='item-search-serial')
        for serial_block in found_serials:
            serial_header = serial_block.find('div', class_='item-search-header').find('a')
            found_serial_name = serial_header.text
            if found_serial_name.lower() == serial_name:
                return {'name': found_serial_name, 'url': serial_header.get('href')}
        return None

    @staticmethod
    def _get_serial_info_by_serial_page(page_data: str) -> dict[str, str]:
        """Информация о сериале со страницы сериала"""
        # todo информирование, если изменилась структура страницы
        soup = BeautifulSoup(page_data, 'lxml')
        last_season_header = soup.find('div', class_="episode-group-name").find("span")
        last_seria_block = soup.find('div', class_="item-serial")
        last_seria_title = last_seria_block.find("div", class_="field-title").find("a")
        return {
            "last_season": last_season_header.text,
            "last_seria_url": last_seria_title.get("href")
        }

    @staticmethod
    def _get_seria_by_seria_page(page_data: str) -> Seria | None:
        """Получение инфо о серии со страницы серии"""
        # todo информирование, если изменилась структура страницы
        seria_release = "Нет информации"
        seria_voices = []
        soup = BeautifulSoup(page_data, 'lxml')
        seria_title = soup.find("div", class_="title-links-wrapper clearfix").find('h1', class_='page-title')
        if seria_description_block := soup.find("div", class_="serial-box-description-torrent"):
            if release_description := seria_description_block.find("div", class_="date-time-description"):
                seria_release = release_description.text
        if voices_block := soup.find("div", class_="sounds-wrapper"):
            if voices_list := voices_block.find("div", class_="sounds-list"):
                seria_voices = [voice.text for voice in voices_list.find_all("div") if voice.text != "Смотреть онлайн"]
        return Seria(
            name=seria_title.text,
            number="",
            url="",
            release_date=seria_release,
            voices=seria_voices,
        )


async def update_my_seria_url_by_vk(vk_access_token: str) -> bool:
    """
    Установка актуального адреса сайта с сериалами

    :param vk_access_token: ключ доступа для доступа к VK API (пользовательский, сообщества или сервисный)
    """
    method_name = 'groups.getById'
    params = {'group_id': 200719078,
              'fields': 'site',
              'access_token': vk_access_token,
              'v': '5.131'
              }
    # Описание метода: https://dev.vk.com/ru/method/groups.getById
    vk_api_url = f'https://api.vk.com/method/{method_name}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=vk_api_url, params=params) as response:
            group = await response.json()
        my_seria_url = group.get('response', [{}])[0].get('site')
        try:
            my_seria_site = SerialSite(MY_SERIA, my_seria_url)
        except ValueError:
            return False

        if await url_is_active(my_seria_site.url):
            return await my_seria_site.save()
    return False
