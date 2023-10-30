from typing import AsyncIterator

from aiogram.utils.markdown import hlink, hbold

from database.models import User
from .my_seria import FindSerialsHelper, MySeriaService


class UserController:
    _my_seria_service_class = MySeriaService

    def __init__(self, user_id: int):
        self.user_id = user_id
        self._user = None
        self.my_seria_service = self._my_seria_service_class()

    async def get_user(self) -> User:
        if self._user is None:
            self._user = await User.get_object(self.user_id)
        return self._user

    async def reboot(self) -> bool:
        """Очистить список сериалов пользователя"""
        user = await self.get_user()
        user.serials = {}
        return await user.save()

    async def get_user_serials(self) -> list[str]:
        """Получить список отслеживаемых сериалов"""
        user = await self.get_user()
        return sorted(serial_name for serial_name in user.serials.keys())

    async def add_serial(self, serial_name: str) -> bool:
        """Добавить сериал в список отслеживаемых"""
        user = await self.get_user()
        if serial_name in user.serials:
            return True
        if await self.my_seria_service.exist(serial_name):
            user.serials.add(serial_name)
            return await user.save()
        return False

    async def delete_serial(self, serial_name: str) -> bool:
        """Убрать сериал из списка отслеживаемых"""
        user = await self.get_user()
        if user.serials.pop(serial_name, None):
            return await user.save()
        return False

    async def get_serial_info(self, serial_name: str) -> str:
        serial = await self.my_seria_service.get_serial_info(serial_name)
        if serial is None:
            return f"Не удалось получить информацию о сериале {serial_name}, попробуйте позже."
        last_seria = serial.last_seria
        return (f'{hbold("Информация о сериале:")}\n{hlink(serial.name, serial.url)}\n'
                f'{hbold("Последний сезон:")} {serial.last_season}\n'
                f'{hbold("Последняя серия:")}\n{hlink(last_seria.full_name, last_seria.url)}\n'
                f'{hbold("Дата выхода серии:")}\n{last_seria.release_date}\n'
                f'{hbold("Вышедшие озвучки:")}\n{", ".join(last_seria.voices)}\n')

    async def get_new_series(self, search: str = None) -> AsyncIterator[str]:
        """Получить информацию о новых сериях"""
        user = await self.get_user()
        serials = user.serials.filter(search)
        is_have_new_series = False
        find_helper = FindSerialsHelper(serials)
        async for seria in self.my_seria_service.get_new_series(find_helper):
            is_have_new_series = True
            yield (f'{hbold("Серия:")}\n{hlink(seria.full_name, seria.url)}\n'
                   f'{hbold("Дата выхода серии:")}\n{seria.release_date}\n'
                   f'{hbold("Вышедшие озвучки:")}\n{", ".join(seria.voices)}\n')
        # todo костыль: получаем юзера заново, чтобы избежать конфликтов, когда с serials работали во время сбора инфо
        user = await self.get_user()
        user.serials.actualize(serials)
        await user.save()
        if not is_have_new_series:
            yield 'Новые серии не найдены.'
