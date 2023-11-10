from __future__ import annotations

import abc
import itertools
from collections import UserDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import AsyncIterator, Iterator


@dataclass(frozen=True)
class Seria:
    """Информация о серии Сериала"""
    name: str
    url: str
    release_date: str
    voices: list[str]


@dataclass(frozen=True)
class Serial:
    """Информация о сериале"""
    name: str
    url: str
    last_season: str
    last_seria: Seria


class UserSerials(UserDict):
    """Управление списком сериалов пользователя"""

    def __contains__(self, key: str) -> bool:
        key = key.strip().capitalize()
        return super().__contains__(key)

    def __getitem__(self, key: str):
        key = key.strip().capitalize()
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: str | datetime) -> None:
        key = key.strip().capitalize()
        if isinstance(value, str):
            try:
                super().__setitem__(key, datetime.strptime(value, '%d.%m.%Y'))
                return
            except ValueError:
                raise ValueError('last_update_date must be stringformat %d.%m.%Y')
        elif isinstance(value, datetime):
            super().__setitem__(key, value.replace(minute=0, hour=0, second=0, microsecond=0))
            return
        raise ValueError('last_update_date must be datetime object or stringformat %d.%m.%Y')

    def actualize(self, serials: UserSerials):
        """Для сериалов, у которых запрашивались новинки обновляем дату последнего обновления на сегодняшнюю"""
        for serial_name in serials.keys():
            if serial_name in self:
                self[serial_name] = datetime.today()

    def add(self, key):
        """Добавление нового сериала"""
        self[key] = datetime.now() - timedelta(days=7)  # Устанавливаем last_update_date с запасом

    def filter(self, key: str | None = None) -> UserSerials:
        if key is None:
            return self
        elif key in self:
            return self.__class__({key: self[key]})
        return self.__class__()

    def group_by_date(self) -> Iterator[tuple[datetime, set[str]]]:
        serials_by_last_update_date = sorted(self.keys(), key=lambda x: self[x], reverse=True)
        for last_date, serials in itertools.groupby(serials_by_last_update_date, key=lambda x: self[x]):
            yield last_date, set(serials)


class BaseSerialService(abc.ABC):
    """Базовый класс для создания сервисов по получению информации о сериалах с сайтов"""

    def __init__(self):
        self.headers = self._get_headers()

    @staticmethod
    def _get_headers():
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/118.0.0.0 Safari/537.36'
        return {'user-agent': user_agent}

    @abc.abstractmethod
    async def get_host(self) -> str:
        """Получение адреса сайта из бд"""
        ...

    @abc.abstractmethod
    async def exist(self, serial_name: str) -> bool:
        """Проверить, есть ли сериал с таким названием"""
        ...

    @abc.abstractmethod
    async def get_serial_info(self, serial_name: str) -> Serial | None:
        """Получить информацию о сериале"""
        ...

    @abc.abstractmethod
    async def get_new_series(self, serials: UserSerials) -> AsyncIterator[Seria]:
        """Получить информацию о новых сериях"""
        yield ...
