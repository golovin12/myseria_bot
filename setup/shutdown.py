import logging

from config import settings

logger = logging.getLogger(__name__)


async def shutdown() -> None:
    try:
        await settings.aioredis.aclose()

        for bot in settings.user_bots.values():
            await bot.on_shutdown()

        if settings.USE_NGROK:
            from pyngrok import ngrok
            ngrok.disconnect(settings.BASE_URL)
    except Exception as e:
        logger.exception(e)
