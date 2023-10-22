import re
from datetime import datetime
from typing import AsyncIterator, Iterator, Any

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from consts import MY_SERIA_KEY
from database.models import SerialSite
from utils import get_date_by_localize_date_string
from .serials import FindSerialsHelper, Serial, Seria


# todo отделить логику парсинга и запросы в сеть

class MySeriaService:
    _user_agent_class = UserAgent

    # todo можно добавить кэш для страниц. Кэш сегодняшней страницы хранится 1 час, остальных страниц - 12 часов.
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
        """Получить список новых серий у сериала с выбранной конкретной даты"""
        async with aiohttp.ClientSession() as session:
            page_data = await self._find_serial_on_site(session, serial_name)
            serial_data = self._find_serial_by_search_page(page_data, serial_name)
            serial_url = serial_data.get('url')
            if not serial_url:
                return None
            # Получение недостающей информации о сериале
            async with session.get(url=serial_url, headers=self.headers) as response:
                serial_page_data = await response.text()
            additional_data = self._get_serial_info_by_serial_page(serial_page_data)
            last_seria_url = additional_data.get('last_seria_url')
            if not last_seria_url:
                return None
            # Получение информации о последней серии
            async with session.get(url=last_seria_url, headers=self.headers) as response:
                seria_page_data = await response.text()
        last_seria = self._get_seria_by_seria_page(seria_page_data, last_seria_url)
        if last_seria:
            return Serial(name=serial_data['name'],
                          url=serial_url,
                          last_season=additional_data.get('last_season', '-'),
                          last_seria=last_seria
                          )
        return None

    async def get_new_series_from_date(self, find_serials_helper: FindSerialsHelper) -> AsyncIterator[Seria]:
        """Получить информацию о сериале"""
        # 2 точки выхода: 1) превышен лимит в 120 страниц; 2) все сериалы были просмотрены (StopIteration)
        try:
            host = await SerialSite(MY_SERIA_KEY).get_url()
            page = 1
            last_date_iterator = find_serials_helper.get_date_and_update_serials()
            last_date = next(last_date_iterator)
            async with aiohttp.ClientSession() as session:
                while page < 120:
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
                            if seria['name'].capitalize() in find_serials_helper.serials:
                                yield Seria(**seria, release_date=series_date.strftime("%d.%m.%Y"))
                    page += 1
        except StopIteration:
            pass

    async def _find_serial_on_site(self, session: aiohttp.ClientSession, serial_name: str) -> str:
        """Поисковый запрос на поиск сериала"""
        # todo информирование, если изменилась структура запроса / сайт не работает
        serial_search_name = re.sub(' ', '+', serial_name)
        host = await SerialSite(MY_SERIA_KEY).get_url()
        url = f'{host}/?do=search&subaction=search&story={serial_search_name}'
        async with session.get(url=url, headers=self.headers) as response:
            page_data = await response.text()
        return page_data

    @staticmethod
    def _get_series_by_series_block(series_block: BeautifulSoup) -> Iterator[dict[str, Any]]:
        """Получить информацию о сериях из блока с сериями"""
        # todo информирование, если изменилась структура страницы
        series_items = series_block.find_all('div', class_="item")
        for seria_item in series_items:
            seria_bottom = seria_item.find('div', class_="serial-bottom")
            if seria_bottom:
                seria_link = seria_bottom.find('a')
                name = re.sub(r' \d{4}$', '', seria_link.text.strip())
                url = seria_link.get("href")
                voices = [voice.text for voice in seria_item.find('div', class_="serial-translate").find_all('a')]
                yield {'name': name, 'url': url, 'voices': voices}

    @staticmethod
    def _get_date_from_series_block(series_block: BeautifulSoup) -> datetime:
        """Получить дату из блока с сериями"""
        # todo информирование, если изменилась структура страницы
        date_text = series_block.find('div', class_="episode-group-name").find("span").text
        return get_date_by_localize_date_string(date_text)

    @staticmethod
    def _find_serial_by_search_page(page_data: str, serial_name: str) -> dict[str, str]:
        """Проверяет, есть ли нужный сериал среди найденных"""
        # todo информирование, если изменилась структура страницы
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

    @staticmethod
    def _get_serial_info_by_serial_page(page_data: str) -> dict[str, str]:
        """Информация о сериале со страницы сериала"""
        # todo информирование, если изменилась структура страницы
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

    @staticmethod
    def _get_seria_by_seria_page(page_data: str, last_seria_url: str) -> Seria | None:
        """Получение инфо о серии со страницы серии"""
        # todo информирование, если изменилась структура страницы
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
