from asyncio import sleep
from datetime import datetime
from typing import AsyncIterator, AsyncIterable, TypeVar

T = TypeVar('T')


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
                await sleep(limit_seconds - seconds_after_start)
        else:
            start_time = datetime.now()
            count = 0
        yield message
        count += 1
