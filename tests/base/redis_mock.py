from unittest.mock import AsyncMock


class AioredisMock(AsyncMock):
    """Мок методов redis, которые используются в database.models"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis_strings: dict[str, str] = {}
        self._redis_sets: dict[str, set[str]] = {}

    async def get(self, key):
        return self._redis_strings.get(key)

    async def set(self, key, value):
        self._redis_strings[key] = value
        return True

    async def sismember(self, key, value):
        return value in self._redis_sets.get(key, set())

    async def smembers(self, key):
        return self._redis_sets.get(key, set())

    async def sadd(self, key, value):
        key_set = self._redis_sets.setdefault(key, set())
        if value not in key_set:
            key_set.add(value)
            return True
        return False

    async def srem(self, key, value):
        key_set = self._redis_sets.setdefault(key, set())
        if value in key_set:
            key_set.remove(value)
            return True
        return False

    async def flushdb(self):
        self._redis_strings = {}
        self._redis_sets = {}
        return True
