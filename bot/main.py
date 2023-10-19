import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from bot.admin.handlers import router as admin_router
from bot.user.handler_paginator import router as pagination_router
from bot.user.handlers import router as user_router
from config import TOKEN, aioredis, storage

dp = Dispatcher(storage=storage)


@dp.shutdown()
async def shutdown():
    try:
        await aioredis.aclose()
        await dp.storage.close()
    except Exception as e:
        print('shutdown_error:', e)


async def main():
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(True)
    dp.include_routers(admin_router, pagination_router, user_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
