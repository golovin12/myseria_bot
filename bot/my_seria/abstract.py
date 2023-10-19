from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, AsyncIterator

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


class FindSerialsHelper:
    def __init__(self, serials: dict):
        self._all_serials = serials
        self.serials = set()
        self.search_dates = dict()
        self._fill_data()

    def _fill_data(self):
        for serial_name, last_date in self._all_serials.items():
            self.serials.add(serial_name)
            self.search_dates.setdefault(datetime.strptime(last_date, "%d.%m.%Y"), set()).add(serial_name)

    def get_date_and_update_serials(self) -> Iterator:
        """При запросе новой даты обновляет список сериалов"""
        for last_date, serials in sorted(self.search_dates.items()):
            yield last_date
            self.serials -= serials  # Удаляем сериалы, которые были привязаны к данной дате


class ExternalService:
    user_agent: UserAgent

    async def exist(self, serial_name: str) -> bool:
        """Проверяет, есть ли сериал с таким названием"""
        ...

    async def get_new_series_from_date(self, find_serials_helper: FindSerialsHelper) -> AsyncIterator[Seria]:
        """Получить список новых серий у сериала с выбранной конкретной даты"""
        yield ...

    async def get_serial_info(self, serial_name: str) -> [Serial | None]:
        """Получить информацию о сериале"""
        ...
