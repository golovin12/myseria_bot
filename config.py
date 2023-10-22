import os
from typing import Any

import redis
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Update
from dotenv import load_dotenv

load_dotenv('.env')

redis_host = os.getenv("REDIS_HOST", 'localhost')
aioredis = redis.asyncio.Redis(host=redis_host, db=1, decode_responses=True)

MY_SERIA_BOT_TOKEN = os.getenv("MY_SERIA_BOT_TOKEN", "")
my_seria_bot_storage = RedisStorage(redis.asyncio.Redis(host=redis_host, db=2, decode_responses=True))
my_seria_bot = Bot(MY_SERIA_BOT_TOKEN, parse_mode=ParseMode.HTML)
my_seria_dp = Dispatcher(storage=my_seria_bot_storage)

ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "")
admin_bot = Bot(ADMIN_BOT_TOKEN, parse_mode=ParseMode.HTML)
admin_dp = Dispatcher()

ADMIN_ID = os.getenv("ADMIN_ID", "")

SECRET_TOKEN = os.getenv("SECRET_TOKEN")

USE_NGROK = os.environ.get("USE_NGROK", "False") == "True"

HOST = '127.0.0.1'
PORT = 8000
BASE_URL = f"https://{HOST}"  # если env.USE_NGROK = True, то BASE_URL заменяется на выданный ngrok


async def admin_bot_process_new_updates(data: dict[Any, Any]) -> None:
    update = Update.model_validate(data, context={"bot": admin_bot})
    await admin_dp.feed_update(admin_bot, update)


async def my_seria_bot_process_new_updates(data: dict[Any, Any]) -> None:
    update = Update.model_validate(data, context={"bot": my_seria_bot})
    await my_seria_dp.feed_update(my_seria_bot, update)
