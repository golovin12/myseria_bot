import os

import redis
from dotenv import load_dotenv

from base_bot import BaseBot

load_dotenv('.env')

REDIS_HOST = os.getenv("REDIS_HOST", 'localhost')
aioredis = redis.asyncio.Redis(host=REDIS_HOST, db=1, decode_responses=True)

ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "")
MY_SERIA_BOT_TOKEN = os.getenv("MY_SERIA_BOT_TOKEN", "")
ZETFLIX_BOT_TOKEN = os.getenv("ZETFLIX_BOT_TOKEN", "")

user_bots: dict[str, BaseBot] = {}

ADMIN_ID = os.getenv("ADMIN_ID", "")

SECRET_TOKEN = os.getenv("SECRET_TOKEN")

SKIP_UPDATES = os.environ.get("SKIP_UPDATES", "True") == "False"

VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")

USE_NGROK = os.environ.get("USE_NGROK", "False") == "True"

HOST = '127.0.0.1'
PORT = 8000
BASE_URL = f"https://{HOST}"  # если env.USE_NGROK = True, то BASE_URL заменяется на выданный ngrok
