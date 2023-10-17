import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterable

import aiohttp
import redis
from aiogram.utils.markdown import hlink, hbold

from my_seria_parcer import ExternalService


class AdminController:
    def __init__(self, aioredis: redis.asyncio.Redis, key_url: str):
        self.aioredis = aioredis
        self.key_url = key_url

    async def force_update_url(self, new_url: str) -> bool:
        new_url = new_url.strip().rstrip("/")
        if re.fullmatch(r'^https?://.*$', new_url):
            async with aiohttp.request("GET", new_url) as resp:
                if resp.status == 200:
                    await self.aioredis.set(self.key_url, new_url)
                    return True
        return False


@dataclass
class Seria:
    name: str
    url: str
    release_date: str
    voices: list[str]


class UserController:
    aioredis: redis.asyncio.Redis
    prefix: str
    external_service: ExternalService

    def __init__(self, user_id: int):
        """
        Формат данных в хранилище:

        {"{user_id}_{prefix}": json.dumps({
            serial_name1: %d.%m.%Y %H:%M,
            serial_name2: %d.%m.%Y %H:%M,
            })}
        """
        self.user_id = user_id
        self._redis_key = f"{self.user_id}_{self.prefix}"

    async def create_if_not_exist(self) -> None:
        """Добавить запись о пользователе, если её ещё нет"""
        await self.aioredis.setnx(self._redis_key, "{}")

    async def reboot(self):
        await self._del_serials()

    async def get_serials(self) -> dict:
        """Получить список отслеживаемых сериалов"""
        user_serials = await self.aioredis.get(self._redis_key)
        if user_serials:
            return json.loads(user_serials)
        return {}

    async def _set_serials(self, serials: dict) -> None:
        """Изменить список отслеживаемых сериалов"""
        await self.aioredis.set(self._redis_key, json.dumps(serials))

    async def _del_serials(self) -> None:
        """Очистить список отслеживаемых сериалов"""
        await self.aioredis.set(self._redis_key, '{}')

    async def add_serial(self, serial: str) -> str:
        """Добавить сериал в список отслеживаемых"""
        if await self.external_service.exist(serial):
            serials = await self.get_serials()
            serials[serial] = datetime.now().strftime('%d.%m.%Y %H:%M')
            await self._set_serials(serials)
            return f"Сериал {serial} был успешно добавлен!\nМожете указать название другого сериала для добавления."
        return ("Вы указали не корректное имя сериала (Имя сериала должно точно совпадать с именем на сайте MySeria)\n"
                f"Сериал, который не вышло добавить: {serial}")

    async def delete_serial(self, serial: str) -> tuple[str, bool]:
        """Убрать сериал из списка отслеживаемых"""
        serials = await self.get_serials()
        if serials.pop(serial, None):
            await self._set_serials(serials)
            return f"Сериал {serial} был успешно удален!\nМожете выбрать ещё сериал для удаления.", True
        return f"Не удалось удалить сериал {serial}, т.к. он не найден в списке отслеживаемых сериалов", False

    async def get_new_series(self, search: str) -> AsyncIterable[str]:
        """Получить информацию о новых сериях"""
        serials = await self._get_filtered_serials(search)
        is_have_new_series = False
        for serial_name, last_search_date in serials.items():
            async for seria_data in self._get_new_series_from_date(serial_name, last_search_date):
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

    async def _get_new_series_from_date(self, serial_name: str, last_search_date: str) -> AsyncIterable[str]:
        """Получить инфо о новых сериях сериала с определённого промежутка времени"""
        search_date = datetime.strptime(last_search_date, '%d.%m.%Y %H:%M')
        try:
            async for seria in self.external_service.get_new_series_from_date(serial_name, search_date):
                yield (f'{hbold("Серия:")}\n{hlink(seria.name, seria.url)}\n'
                       f'{hbold("Дата выхода серии:")}\n{seria.release_date}\n'
                       f'{hbold("Вышедшие озвучки:")}\n{", ".join(seria.voices)}\n')
        except:
            yield f'При попытке получения информации о сериале "{serial_name}" произошла ошибка, попробуйте ещё раз.'