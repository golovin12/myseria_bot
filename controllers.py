import json
import re
from datetime import timedelta, datetime
from typing import AsyncIterator, Type, Iterable

import aiohttp
import redis
from aiogram.utils.markdown import hlink, hbold

from utils import FindSerialsHelper, ExternalService


class AdminController:
    def __init__(self, aioredis: redis.asyncio.Redis, key_url: str):
        self.aioredis = aioredis
        self.key_url = key_url

    async def force_update_url(self, new_url: str) -> bool:
        new_url = new_url.strip().rstrip("/")
        if re.fullmatch(r'^https?://.*$', new_url):
            async with aiohttp.request("GET", new_url) as response:
                if response.status == 200:
                    await self.aioredis.set(self.key_url, new_url)
                    return True
        return False


class UserController:
    aioredis: redis.asyncio.Redis
    prefix: str
    external_service_class: Type[ExternalService]

    def __init__(self, user_id: int):
        """
        Формат данных в хранилище:

        {"{user_id}_{prefix}": json.dumps({
            serial_name1: %d.%m.%Y,
            serial_name2: %d.%m.%Y,
            })}
        """
        self.user_id = user_id
        self._redis_key = f"{self.user_id}_{self.prefix}"
        self._external_service = self.external_service_class()

    async def create_if_not_exist(self) -> None:
        """Добавить запись о пользователе, если её ещё нет"""
        await self.aioredis.setnx(self._redis_key, "{}")

    async def reboot(self) -> None:
        await self._del_serials()

    async def get_serials(self) -> dict:
        """Получить список отслеживаемых сериалов"""
        serials = await self.aioredis.get(self._redis_key)
        if serials:
            return json.loads(serials)
        return {}

    async def _set_serials(self, serials: dict) -> None:
        """Изменить список отслеживаемых сериалов"""
        await self.aioredis.set(self._redis_key, json.dumps(serials))

    async def _del_serials(self) -> None:
        """Очистить список отслеживаемых сериалов"""
        await self.aioredis.set(self._redis_key, '{}')

    async def add_serial(self, serial_name: str) -> bool:
        """Добавить сериал в список отслеживаемых"""
        serial_name = serial_name.capitalize()
        serials = await self.get_serials()
        if serial_name in serials:
            return True
        if await self._external_service.exist(serial_name):
            serials[serial_name] = (datetime.today() - timedelta(days=7)).strftime('%d.%m.%Y')
            await self._set_serials(serials)
            return True
        return False

    async def delete_serial(self, serial_name: str) -> bool:
        """Убрать сериал из списка отслеживаемых"""
        serial_name = serial_name.capitalize()
        serials = await self.get_serials()
        if serials.pop(serial_name, None):
            await self._set_serials(serials)
            return True
        return False

    async def get_serial_info(self, serial_name: str) -> str:
        serial = await self._external_service.get_serial_info(serial_name)
        if not serial:
            return f"Не удалось получить информацию о сериале {serial_name}, попробуйте позже."
        last_seria = serial.last_seria
        return (f'{hbold("Информация о сериале:")}\n{hlink(serial.name, serial.url)}\n'
                f'{hbold("Последний сезон:")} {serial.last_season}\n'
                f'{hbold("Последняя серия:")}\n{hlink(last_seria.name, last_seria.url)}\n'
                f'{hbold("Дата выхода серии:")}\n{last_seria.release_date}\n'
                f'{hbold("Вышедшие озвучки:")}\n{", ".join(last_seria.voices)}\n')

    async def get_new_series(self, search: str) -> AsyncIterator[str]:
        """Получить информацию о новых сериях"""
        serials = await self._get_filtered_serials(search)
        is_have_new_series = False
        async for seria_data in self._get_new_series_by_date(serials):
            is_have_new_series = True
            yield seria_data
        if not is_have_new_series:
            yield 'Новые серии не найдены.'

    async def _get_filtered_serials(self, search: str) -> dict:
        """Получить отфильтрованный список отслеживаемых сериалов"""
        serials = await self.get_serials()
        if search == '__all__':
            return serials
        elif search not in serials:
            return {}
        return {search: serials[search]}

    async def _get_new_series_by_date(self, serials: dict) -> AsyncIterator[str]:
        """Получить инфо о новых сериях сериала с выбранной даты"""
        find_helper = FindSerialsHelper(serials)
        async for seria in self._external_service.get_new_series_from_date(find_helper):
            yield (f'{hbold("Серия:")}\n{hlink(seria.name, seria.url)}\n'
                   f'{hbold("Дата выхода серии:")}\n{seria.release_date}\n'
                   f'{hbold("Вышедшие озвучки:")}\n{", ".join(seria.voices)}\n')
        await self._update_serials_last_date(serials)

    async def _update_serials_last_date(self, update_serials: Iterable) -> None:
        """Для сериалов, у которых запрашивались новинки обновляем дату последнего обновления на сегодняшнюю"""
        serials = await self.get_serials()
        for serial_name in update_serials:
            serials[serial_name] = datetime.today().strftime("%d.%m.%Y")
        await self._set_serials(serials)
