import re
from typing import Iterator

from bs4 import BeautifulSoup

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
        found_serials = self.soup.find_all('a', class_='sres-wrap')
        try:
            for serial_block in found_serials:
                found_serial_name = serial_block.find('div', class_='sres-text').find('h2').text
                if found_serial_name.lower() == serial_name:
                    found_serial_url = serial_block.get('href').strip()
                    if '/serials/' in found_serial_url:  # не включаем в поиск фильмы
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
            last_season = self.soup.find('div', class_="sez-wr").find_all("a")[-1].text
            last_seria_block = self.soup.find('div', class_="video-item")
            last_seria_url = last_seria_block.find("div", class_="vi-in").find("a").get("href")
        except AttributeError:
            raise ParsingError('Ошибка при разборе информации о сериале')
        return last_seria_url, last_season

    def get_series_url(self):
        try:
            for seria in self.soup.find_all('div', class_="video-item"):
                yield seria.find("div", class_="vi-in").find("a").get("href")
        except AttributeError:
            raise ParsingError('Ошибка при разборе информации о сериале')


class SeriaPageParser(BaseParser):
    """Парсер страницы серии"""
    seria_desc_miss = r'(смотреть новую серию )' \
                      r'|( в режиме онлайн, в хорошем качестве, совершенно бесплатно и только на русском языке!)'

    def get_seria_data(self) -> tuple[str, str, list[str]]:
        """Получение инфо о серии"""
        seria_voices = ["..."]  # todo получить озвучки
        seria_release = "Нет информации"
        try:
            seria_name = self.soup.find("meta", attrs={"name": "description"}).get('content')
            seria_name = re.sub(self.seria_desc_miss, '', seria_name)
            if release_description := self.soup.find("meta", attrs={"itemprop": "dateCreated"}):
                seria_release = release_description.get('content') or ''
        except AttributeError:
            raise ParsingError('Ошибка при разборе информации о серии')
        return seria_name, seria_release, seria_voices
