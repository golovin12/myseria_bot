import re
from typing import AsyncIterator

import aiohttp

from common_tools.async_connection import url_is_active
from consts import MySeria, LIMIT_SEARCH_DEPTH
from database.models import SerialSite
from serial_services import BaseSerialService, Serial, Seria, UserSerials
from .parsers import SearchPageParser, SerialPageParser, SeriaPageParser, NewSeriesPageParser


class MySeriaService(BaseSerialService):
    # todo обработка сетевых ошибок
    serial_site_key = MySeria.KEY

    @classmethod
    async def update_url_by_vk(cls, vk_access_token: str) -> bool:
        """
        Получает актуальный адрес сайта со страницы ВК и обновляет его в бд

        :param vk_access_token: ключ доступа для доступа к VK API (пользовательский, сообщества или сервисный)
        """
        method_name = 'groups.getById'
        params = {'group_id': MySeria.VK_GROUP_ID,
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
            my_seria_site = SerialSite(cls.serial_site_key, my_seria_url)
        except ValueError:
            return False

        if await url_is_active(my_seria_site.url):
            return await my_seria_site.save()
        return False

    async def get_host(self) -> str:
        """Получение адреса сайта из бд"""
        my_seria_site = await SerialSite.get_object(self.serial_site_key)
        return my_seria_site.url

    async def get_new_series(self, serials: UserSerials) -> AsyncIterator[Seria]:
        """Получить информацию о новых сериях"""
        host = await self.get_host()
        tracked_serials = set(serials.keys())
        serials_by_last_date = serials.group_by_date()
        # Точки выхода:
        # 1) количество просмотренных страниц превысило лимит;
        # 2) все сериалы были обработаны (StopIteration)
        try:
            last_date, last_date_serials = next(serials_by_last_date)
            async with aiohttp.ClientSession() as session:
                page = 1
                while page < LIMIT_SEARCH_DEPTH:
                    page_url = f'{host}/series/page/{page}/'
                    async with session.get(url=page_url, headers=self.headers) as response:
                        page_data = await response.text()
                    new_series_by_date_iterator = NewSeriesPageParser(page_data).get_series_group_by_date()
                    for series_date, series_by_date in new_series_by_date_iterator:
                        if last_date > series_date:
                            # Удаляем сериалы, которые были привязаны к обработанной дате
                            tracked_serials -= last_date_serials
                            last_date, last_date_serials = next(serials_by_last_date)
                        for seria_data in series_by_date:
                            s_name, s_number, s_url, s_voices = seria_data
                            if s_name.capitalize() in tracked_serials:
                                yield Seria(
                                    name=f'{s_name} {s_number}',
                                    url=s_url,
                                    release_date=series_date.strftime("%d.%m.%Y"),
                                    voices=s_voices,
                                )
                    page += 1
        except StopIteration:
            pass

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

    async def exist(self, serial_name: str) -> bool:
        """Проверяет, есть ли сериал с таким названием"""
        async with aiohttp.ClientSession() as session:
            serial_data = await self._find_serial_on_site(session, serial_name)
        if serial_data:
            return True
        return False

    async def _find_serial_on_site(self, session: aiohttp.ClientSession, serial_name: str) -> tuple[str, str] | None:
        """Запрос на поиск сериала"""
        serial_search_name = re.sub(' ', '+', serial_name)
        host = await self.get_host()
        url = f'{host}/?do=search&subaction=search&story={serial_search_name}'
        async with session.get(url=url, headers=self.headers) as response:
            page_data = await response.text()
        return SearchPageParser(page_data).find_serial_data(serial_name)
