from datetime import timedelta, datetime
from typing import AsyncIterator, Type, Iterable

from aiogram.utils.markdown import hlink, hbold

from bot.consts import CallbackButtonInfo
from bot.database.models import User
from bot.my_seria.abstract import FindSerialsHelper, ExternalService
from bot.my_seria.parser import MySeriaService


class UserController:
    external_service_class: Type[ExternalService]

    def __init__(self, user_id: int):
        self.user = User(user_id)
        self._external_service = MySeriaService()  # todo self.external_service_class()

    async def reboot(self) -> None:
        """Очистить список сериалов пользователя"""
        await self.user.del_serials()

    async def get_serials(self) -> dict:
        """Получить список отслеживаемых сериалов"""
        return await self.user.get_serials()

    async def _set_serials(self, serials: dict) -> None:
        """Изменить список отслеживаемых сериалов"""
        await self.user.set_serials(serials)

    async def add_serial(self, serial_name: str) -> bool:
        """Добавить сериал в список отслеживаемых"""
        serial_name = self._format_serial_name(serial_name)
        serials = await self.get_serials()
        if serial_name in serials:
            return True
        if await self._external_service.exist(serial_name):
            # Задаём дату отслеживания
            serials[serial_name] = (datetime.today() - timedelta(days=7)).strftime('%d.%m.%Y')
            await self._set_serials(serials)
            return True
        return False

    async def delete_serial(self, serial_name: str) -> bool:
        """Убрать сериал из списка отслеживаемых"""
        serial_name = self._format_serial_name(serial_name)
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
        find_helper = FindSerialsHelper(serials)
        async for seria in self._external_service.get_new_series_from_date(find_helper):
            is_have_new_series = True
            yield (f'{hbold("Серия:")}\n{hlink(seria.name, seria.url)}\n'
                   f'{hbold("Дата выхода серии:")}\n{seria.release_date}\n'
                   f'{hbold("Вышедшие озвучки:")}\n{", ".join(seria.voices)}\n')
        await self._update_serials_last_date(serials)
        if not is_have_new_series:
            yield 'Новые серии не найдены.'

    async def _get_filtered_serials(self, search: str) -> dict:
        """Получить отфильтрованный список отслеживаемых сериалов"""
        serials = await self.get_serials()
        if search == CallbackButtonInfo.ALL:
            return serials
        elif search not in serials:
            return {}
        return {search: serials[search]}

    async def _update_serials_last_date(self, update_serials: Iterable) -> None:
        """Для сериалов, у которых запрашивались новинки обновляем дату последнего обновления на сегодняшнюю"""
        serials = await self.get_serials()
        for serial_name in update_serials:
            serials[serial_name] = datetime.today().strftime("%d.%m.%Y")
        await self._set_serials(serials)

    @staticmethod
    def _format_serial_name(serial_name: str) -> str:
        """Имя сериала к общему виду"""
        return serial_name.capitalize()