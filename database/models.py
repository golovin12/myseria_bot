import json

from config import aioredis
from consts import SERIALS_PREFIX, ADMIN_KEY


class SerialSite:
    key: str
    url: str

    def __init__(self, key):
        """
        Доступ к атрибутам через get_ и set_ методы
        """
        self.key = key

    async def get_url(self) -> str:
        url: str = await aioredis.get(self.key)
        return url or 'https://'

    async def set_url(self, url: str):
        await aioredis.set(self.key, url)


class User:
    user_id: int
    serials: dict
    is_admin: bool

    def __init__(self, user_id: int):
        """
        Доступ к атрибутам через get_, set_ и del_ методы

        Формат данных в хранилище:

        "{user_id}_{prefix}": json.dumps(serials)

        admins: set(user_id1, user_id2)
        """
        self.user_id = user_id
        self._redis_serials_key = f"{self.user_id}_{SERIALS_PREFIX}"
        self._redis_admin_key = ADMIN_KEY

    async def get_serials(self) -> dict:
        serials = await aioredis.get(self._redis_serials_key)
        if serials:
            return json.loads(serials)
        return {}

    async def set_serials(self, serials: dict):
        await aioredis.set(self._redis_serials_key, json.dumps(serials))

    async def del_serials(self):
        await aioredis.set(self._redis_serials_key, '{}')

    async def is_admin(self) -> bool:
        is_admin = await aioredis.sismember(self._redis_admin_key, str(self.user_id))
        return is_admin

    async def set_is_admin(self):
        await aioredis.sadd(self._redis_admin_key, str(self.user_id))

    async def del_is_admin(self):
        await aioredis.srem(self._redis_admin_key, str(self.user_id))

    async def get_all_admins(self) -> set[str]:
        return await aioredis.smembers(self._redis_admin_key)
