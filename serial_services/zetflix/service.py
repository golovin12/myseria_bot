import datetime
import re
from typing import AsyncIterator

import aiohttp

from consts import Zetflix
from database.models import SerialSite
from serial_services import BaseSerialService, Serial, Seria, UserSerials
from .parsers import SearchPageParser, SerialPageParser, SeriaPageParser


class ZetflixService(BaseSerialService):
    # todo обработка сетевых ошибок
    serial_site_key = Zetflix.KEY

    @staticmethod
    def _get_headers():
        headers = super(ZetflixService, ZetflixService)._get_headers()
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,' \
                            'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        headers['Referer'] = 'https://www.google.com/'
        return headers

    @classmethod
    async def update_url_by_vk(cls, vk_access_token: str) -> bool:
        """
        Получает актуальный адрес сайта со страницы ВК и обновляет его в бд

        :param vk_access_token: ключ доступа для доступа к VK API (пользовательский, сообщества или сервисный)
        """
        method_name = 'groups.getById'
        params = {'group_id': Zetflix.VK_GROUP_ID,
                  'fields': 'site',
                  'access_token': vk_access_token,
                  'v': '5.131'
                  }
        # Описание метода: https://dev.vk.com/ru/method/groups.getById
        vk_api_url = f'https://api.vk.com/method/{method_name}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url=vk_api_url, params=params) as response:
                group = await response.json()
            zetflix_url = group.get('response', [{}])[0].get('site')

            try:
                zetflix_site = SerialSite(cls.serial_site_key, zetflix_url)
            except ValueError:
                return False
            async with session.get(url=zetflix_url, params=params, headers=cls._get_headers()) as response:
                if response.status == 200:
                    return await zetflix_site.save()
        return False

    async def get_host(self) -> str:
        """Получение адреса сайта из бд"""
        my_seria_site = await SerialSite.get_object(self.serial_site_key)
        return my_seria_site.url

    async def exist(self, serial_name: str) -> bool:
        """Проверяет, есть ли сериал с таким названием"""
        async with aiohttp.ClientSession() as session:
            serial_data = await self._find_serial_on_site(session, serial_name)
        if serial_data:
            return True
        return False

    async def get_serial_info(self, serial_name: str) -> Serial | None:
        """Получить информацию о сериале"""
        serial_name = serial_name.strip()
        async with aiohttp.ClientSession() as session:
            # Поиск сериала
            serial_data = await self._find_serial_on_site(session, serial_name)
            if serial_data is None:
                return None
            serial_url, serial_name = serial_data
            # Получение недостающей информации о сериале
            async with session.get(url=serial_url, headers=self.headers) as response:
                serial_page_data = await response.text()
            last_seria_url, last_season = SerialPageParser(serial_page_data).get_serial_data()
            # Получение информации о последней серии
            async with session.get(url=last_seria_url, headers=self.headers) as response:
                seria_page_data = await response.text()
            seria_name, seria_release, seria_voices = SeriaPageParser(seria_page_data).get_seria_data()
            last_seria = Seria(name=seria_name, url=last_seria_url, release_date=seria_release, voices=seria_voices)
        return Serial(name=serial_name, url=serial_url, last_season=last_season, last_seria=last_seria)

    async def get_new_series(self, serials: UserSerials) -> AsyncIterator[Seria]:
        """Получить информацию о новых сериях"""
        async with aiohttp.ClientSession() as session:
            for s_name, s_last_date in serials.items():
                serial_data = await self._find_serial_on_site(session, s_name)
                if serial_data is None:
                    continue
                serial_url, serial_name = serial_data
                # Получение списка серий
                async with session.get(url=serial_url, headers=self.headers) as response:
                    serial_page_data = await response.text()
                for seria_url in SerialPageParser(serial_page_data).get_series_url():
                    # Получение информации о серии
                    async with session.get(url=seria_url, headers=self.headers) as response:
                        seria_page_data = await response.text()
                    seria_name, seria_release, seria_voices = SeriaPageParser(seria_page_data).get_seria_data()
                    if seria_release and s_last_date > datetime.datetime.fromisoformat(seria_release):
                        break
                    yield Seria(name=seria_name, url=seria_url, release_date=seria_release, voices=seria_voices)

    async def _find_serial_on_site(self, session: aiohttp.ClientSession, serial_name: str) -> tuple[str, str] | None:
        """Запрос на поиск сериала"""
        serial_search_name = re.sub(' ', '+', serial_name)
        host = await self.get_host()
        url = f'{host}/?do=search&subaction=search&story={serial_search_name}'
        async with session.get(url=url, headers=self.headers) as response:
            page_data = await response.text()
        return SearchPageParser(page_data).find_serial_data(serial_name)
