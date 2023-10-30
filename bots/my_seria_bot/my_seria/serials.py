from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

from database.models import Serials


@dataclass
class Seria:
    name: str
    number: str
    url: str
    release_date: str
    voices: list[str]

    @property
    def full_name(self):
        return f'{self.name} {self.number}'


@dataclass(frozen=True)
class Serial:
    name: str
    url: str
    last_season: str
    last_seria: Seria


class FindSerialsHelper:
    def __init__(self, serials: Serials):
        self._serials = serials
        self.unupdated_serials: set[str] = set()
        self.search_dates: dict[datetime, set[str]] = {}
        self._fill_data()

    def _fill_data(self) -> None:
        """Разбирает _serials и заполняет unupdated_serials и search_dates"""
        for serial_name, last_date in self._serials.items():
            self.unupdated_serials.add(serial_name)
            self.search_dates.setdefault(last_date, set()).add(serial_name)

    def get_date_and_update_serials(self) -> Iterator[datetime]:
        """При запросе новой даты обновляет список сериалов (unupdated_serials)"""
        for last_date, serials in sorted(self.search_dates.items(), key=lambda x: x[0], reverse=True):
            yield last_date
            self.unupdated_serials -= serials  # Удаляем сериалы, которые были привязаны к данной дате
