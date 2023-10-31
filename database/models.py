from __future__ import annotations

import abc
import json

from common_tools.json_serializer import dict_date_serializer
from config import aioredis
from serial_services import UserSerials
from .errors import ObjectNotFoundError
from .fields import CharField, UrlField, IntegerField, BooleanField, JsonField


class BaseModel(abc.ABC):
    @classmethod
    @abc.abstractmethod
    async def get_object(cls, pk) -> BaseModel:
        ...

    @abc.abstractmethod
    async def save(self) -> bool:
        ...


class SerialSite(BaseModel):
    name: str = CharField(empty_allowed=False)
    url: str = UrlField()

    @staticmethod
    def _get_redis_key(name: str) -> str:
        return f"{name}_site"

    @classmethod
    async def get_object(cls, name: str) -> SerialSite:
        redis_key = cls._get_redis_key(name)
        url: str = await aioredis.get(redis_key)
        try:
            return cls(name, url)
        except ValueError:
            raise ObjectNotFoundError

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    async def save(self) -> bool:
        """
        Формат данных в хранилище:

        "{name}_site": url
        """
        redis_key = self._get_redis_key(self.name)
        return bool(await aioredis.set(redis_key, self.url))


class User(BaseModel):
    user_id: int = IntegerField()
    serials: UserSerials = JsonField(user_type=UserSerials)

    @staticmethod
    def _get_redis_key_by_user_id(user_id: int) -> str:
        return f"{user_id}_serials"

    @classmethod
    async def _get_user_serials(cls, user_id: int) -> dict:
        redis_key = cls._get_redis_key_by_user_id(user_id)
        serials_str: str = await aioredis.get(redis_key)
        serials = json.loads(serials_str) if serials_str else {}  # Обрабатываем случаи, когда информации о юзере нет
        return serials

    @classmethod
    async def get_object(cls, user_id: int) -> User:
        try:
            serials = await cls._get_user_serials(user_id)
            return cls(user_id, serials)
        except ValueError:
            raise ObjectNotFoundError

    def __init__(self, user_id: int, serials: dict | UserSerials):
        self.user_id = user_id
        self.serials = serials

    async def save(self) -> bool:
        """
        Формат данных в хранилище:

        "{user_id}_serials": json.dumps({serial_name: %d.%m.%Y, ...})
        """
        redis_key = self._get_redis_key_by_user_id(self.user_id)
        return bool(await aioredis.set(redis_key, json.dumps(self.serials, default=dict_date_serializer)))


class Admin(BaseModel):
    user_id: int = IntegerField()
    is_admin: bool = BooleanField()

    @staticmethod
    def _get_redis_key() -> str:
        return "admins"

    @classmethod
    async def get_object(cls, user_id: int) -> Admin:
        redis_key = cls._get_redis_key()
        is_admin = bool(await aioredis.sismember(redis_key, str(user_id)))
        try:
            return cls(user_id, is_admin)
        except ValueError:
            raise ObjectNotFoundError

    @classmethod
    async def get_object_or_none(cls, user_id: int) -> Admin | None:
        try:
            return await cls.get_object(user_id)
        except ObjectNotFoundError:
            return None

    @classmethod
    async def get_admins_id(cls) -> set[str]:
        """Возвращает идентификаторы юзеров с правами администратора"""
        redis_key = cls._get_redis_key()
        return await aioredis.smembers(redis_key)

    def __init__(self, user_id, is_admin):
        self.user_id = user_id
        self.is_admin = is_admin

    async def save(self) -> bool:
        """
        Формат данных в хранилище

        admins: set(user_id, ...)
        """
        redis_key = self._get_redis_key()
        if self.is_admin:
            return bool(await aioredis.sadd(redis_key, str(self.user_id)))
        return bool(await aioredis.srem(redis_key, str(self.user_id)))
