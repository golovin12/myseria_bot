from fastapi import Header, HTTPException, Depends

from config import settings


async def verify_token(x_telegram_bot_api_secret_token: str = Header()):
    if x_telegram_bot_api_secret_token != settings.SECRET_TOKEN:
        raise HTTPException(status_code=422, detail="X-Telegram-Bot-Api-Secret-Token header invalid")


BotPermission = Depends(verify_token)
