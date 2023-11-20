from fastapi import APIRouter, Request

from config import settings
from consts import MySeria, ADMIN_KEY, Zetflix
from .permissions import BotPermission

bot_router = APIRouter(prefix='/bot', dependencies=[BotPermission])


@bot_router.post(f'/{MySeria.KEY}')
async def my_seria_bot(request: Request) -> dict[str, str]:  # noqa F811
    await settings.user_bots[MySeria.KEY].process_new_updates(await request.json())
    return {"ok": "ok"}


@bot_router.post(f'/{Zetflix.KEY}')
async def zetflix_bot(request: Request) -> dict[str, str]:  # noqa F811
    await settings.user_bots[Zetflix.KEY].process_new_updates(await request.json())
    return {"ok": "ok"}


@bot_router.post(f'/{ADMIN_KEY}')
async def admin_bot(request: Request) -> dict[str, str]:  # noqa F811
    """Бот доступен только администраторам"""
    await settings.user_bots[ADMIN_KEY].process_new_updates(await request.json())
    return {"ok": "ok"}
