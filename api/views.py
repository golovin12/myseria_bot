from fastapi import APIRouter, Request

from config import SECRET_TOKEN, admin_bot_process_new_updates, my_seria_bot_process_new_updates
from consts import MY_SERIA_ROUTE, ADMIN_ROUTE
from database.models import Admin

router = APIRouter(prefix='/bot')


@router.post(MY_SERIA_ROUTE)
async def my_seria_bot(request: Request) -> dict[str, str]:  # noqa F811
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') == SECRET_TOKEN:
        await my_seria_bot_process_new_updates(await request.json())
    return {"ok": "ok"}


@router.post(ADMIN_ROUTE)
async def admin_bot(request: Request) -> dict[str, str]:  # noqa F811
    """Бот доступен только администраторам"""
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') == SECRET_TOKEN:
        result = await request.json()
        user_id = result.get('message', {}).get('from').get('id', '')
        admin = await Admin.get_object_or_none(user_id)
        if admin is not None and admin.is_admin:
            await admin_bot_process_new_updates(result)
    return {"ok": "ok"}