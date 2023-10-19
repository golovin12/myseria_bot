import os

import redis
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv

load_dotenv('.env')

TOKEN = os.getenv("BOT_TOKEN")
aioredis = redis.asyncio.Redis(db=1, decode_responses=True)
storage = RedisStorage(redis.asyncio.Redis(db=2, decode_responses=True))
