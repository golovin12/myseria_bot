from fastapi import APIRouter, Request

from config import settings
from consts import MySeria, ADMIN_KEY, Zetflix
from database.models import Admin
from .permissions import BotPermission

bot_router = APIRouter(prefix='/bot', dependencies=[BotPermission])


@bot_router.post(f'/{MySeria.KEY}')
async def my_seria_bot(request: Request) -> dict[str, str]:  # noqa F811
    await settings.user_bots[MySeria.KEY].process_new_updates(await request.json())
    return {"ok": "ok"}


@bot_router.post(f'/{Zetflix.KEY}')
async def my_seria_bot(request: Request) -> dict[str, str]:  # noqa F811
    await settings.user_bots[Zetflix.KEY].process_new_updates(await request.json())
    return {"ok": "ok"}


@bot_router.post(f'/{ADMIN_KEY}')
async def admin_bot(request: Request) -> dict[str, str]:  # noqa F811
    """Бот доступен только администраторам"""
    result = await request.json()
    msg = result.get('message') or result.get('callback_query', {})
    user_id = msg.get('from', {}).get('id', '')
    admin = await Admin.get_object_or_none(user_id)
    if admin is not None and admin.is_admin:
        await settings.user_bots[ADMIN_KEY].process_new_updates(result)
    return {"ok": "ok"}
