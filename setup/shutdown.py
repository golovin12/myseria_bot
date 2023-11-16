import logging

from config import settings

logger = logging.getLogger(__name__)


async def shutdown() -> None:
    try:
        for bot in settings.user_bots.values():
            await bot.on_shutdown()

        await settings.aioredis.aclose()

        if settings.USE_NGROK:
            from pyngrok import ngrok
            ngrok.disconnect(settings.BASE_URL)
    except Exception as e:
        logger.exception(e)
