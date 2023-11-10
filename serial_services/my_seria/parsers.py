import re
from datetime import datetime
from typing import Iterator

from bs4 import BeautifulSoup

from common_tools.date import get_date_by_localize_string
from ..errors import ParsingError

SeriaInfoIterator = Iterator[tuple[str, str, str, list[str]]]


class BaseParser:
    def __init__(self, page_data: str):
        self.soup = BeautifulSoup(page_data, "lxml")


class SearchPageParser(BaseParser):
    """Парсер страницы поиска"""

    def find_serial_data(self, serial_name: str) -> tuple[str, str] | None:
        """
        Найти сериал на странице поиска.

        :param serial_name: Название сериала который нужно найти.

        :return: (found_serial_url, found_serial_name) | None
        """
        serial_name = serial_name.lower()
        found_serials = self.soup.find_all('div', class_='item-search-serial')
        try:
            for serial_block in found_serials:
                serial_header = serial_block.find('div', class_='item-search-header').find('a')
                found_serial_name = serial_header.text
                if found_serial_name.lower() == serial_name:
                    found_serial_url = serial_header.get('href').strip()
                    return found_serial_url, found_serial_name
        except AttributeError:
            raise ParsingError('Ошибка при поиске сериала')
        return None


class SerialPageParser(BaseParser):
    """Парсер страницы сериала"""

    def get_serial_data(self) -> tuple[str, str]:
        """
        Информация о сериале со страницы сериала

        :return: last_seria_url, last_season
        """
        try:
            last_season = self.soup.find('div', class_="episode-group-name").find("span").text
            last_seria_block = self.soup.find('div', class_="item-serial")
            last_seria_url = last_seria_block.find("div", class_="field-title").find("a").get("href")
        except AttributeError:
            raise ParsingError('Ошибка при разборе информации о сериале')
        return last_seria_url, last_season


class SeriaPageParser(BaseParser):
    """Парсер страницы серии"""

    def get_seria_data(self) -> tuple[str, str, list[str]]:
        """Получение инфо о серии"""
        seria_voices = []
        seria_release = "Нет информации"
        try:
            seria_box = self.soup.find("div", "box-serial-series-top")
            seria_title = seria_box.find("div", class_="title-links-wrapper clearfix").find('h1', class_='page-title')
            seria_name = seria_title.text
            if voices_block := seria_box.find("div", class_="sounds-wrapper"):
                voices = voices_block.find("div", class_="sounds-list").find_all("div")
                seria_voices = [voice.text for voice in voices if voice.text != "Смотреть онлайн"]
            if seria_description_block := self.soup.find("div", class_="serial-box-description-torrent"):
                if release_description := seria_description_block.find("div", class_="date-time-description"):
                    seria_release = release_description.text
        except AttributeError:
            raise ParsingError('Ошибка при разборе информации о серии')
        return seria_name, seria_release, seria_voices


class NewSeriesPageParser(BaseParser):
    """Парсер страницы новых серий"""

    def get_series_group_by_date(self) -> Iterator[tuple[datetime, SeriaInfoIterator]]:
        """Получить дату из блока с сериями"""
        try:
            for series_block in self.soup.find_all('div', class_="episode-group"):
                date_text = series_block.find('div', class_="episode-group-name").find("span").text
                date = get_date_by_localize_string(date_text)
                yield date, self._get_series_info(series_block)
        except (AttributeError, ValueError, TypeError):
            raise ParsingError('Ошибка при разборе информации о серии')

    def _get_series_info(self, series_block: BeautifulSoup) -> SeriaInfoIterator:
        """Получить информацию о сериях из блока с сериями"""
        series_items = series_block.find_all('div', class_="item")
        for seria_item in series_items:
            seria_bottom = seria_item.find('div', class_="serial-bottom")
            seria_title = seria_bottom.find('div', class_="field-title").find('a')
            number = seria_bottom.find('div', class_="field-description").find('a').text
            name = re.sub(r' \d{4}$', '', seria_title.text.strip())
            url = seria_title.get("href")
            voices = [voice.text for voice in seria_item.find('div', class_="serial-translate").find_all('a')]
            yield name, number, url, voices
