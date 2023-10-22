import asyncio
from datetime import datetime
from itertools import islice
from typing import Iterable, AsyncIterable, AsyncIterator, Iterator, TypeVar

from consts import MONTH_NAMES_RU

T = TypeVar('T')


def batched(iterable: Iterable[T], n: int) -> Iterator[tuple[T]]:
    """
    >>> batched([1, 2, 3, 4, 5], 2)
    [1, 2] [3, 4] [5]
    """
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


async def message_per_seconds_limiter(async_generator: AsyncIterable[T], limit_messages: int = 15,
                                      limit_seconds: int = 60) -> AsyncIterator[T]:
    """
    Ограничивает частоту отправки сообщений. Ограничение limit_messages/limit_seconds (количество сообщений/n секунд)
    """
    start_time = datetime.now()
    count = 0
    async for message in async_generator:
        seconds_after_start = (datetime.now() - start_time).seconds
        if seconds_after_start <= limit_seconds:
            if count > limit_messages:
                await asyncio.sleep(limit_seconds - seconds_after_start)
        else:
            start_time = datetime.now()
            count = 0
        yield message
        count += 1


def get_date_by_localize_date_string(date_string: str) -> datetime:
    """Формирует дату из строки вида: 29 сентября 2019"""
    day, month, year = date_string.split()
    month_num = MONTH_NAMES_RU[month]
    return datetime(day=int(day), month=month_num, year=int(year))
