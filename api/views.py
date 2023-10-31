from fastapi import APIRouter, Request

from config import SECRET_TOKEN, user_bots
from consts import MySeria, ADMIN_KEY, Zetflix
from database.models import Admin

router = APIRouter(prefix='/bot')


@router.post(f'/{MySeria.KEY}')
async def my_seria_bot(request: Request) -> dict[str, str]:  # noqa F811
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') == SECRET_TOKEN:
        await user_bots[MySeria.KEY].process_new_updates(await request.json())
    return {"ok": "ok"}


@router.post(f'/{Zetflix.KEY}')
async def my_seria_bot(request: Request) -> dict[str, str]:  # noqa F811
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') == SECRET_TOKEN:
        await user_bots[Zetflix.KEY].process_new_updates(await request.json())
    return {"ok": "ok"}


@router.post(f'/{ADMIN_KEY}')
async def admin_bot(request: Request) -> dict[str, str]:  # noqa F811
    """Бот доступен только администраторам"""
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') == SECRET_TOKEN:
        result = await request.json()
        user_id = result.get('message', {}).get('from').get('id', '')
        admin = await Admin.get_object_or_none(user_id)
        if admin is not None and admin.is_admin:
            await user_bots[ADMIN_KEY].process_new_updates(await request.json())
    return {"ok": "ok"}
