import logging

import config

logger = logging.getLogger(__name__)


async def shutdown() -> None:
    try:
        await config.aioredis.aclose()

        for bot in config.user_bots.values():
            await bot.on_shutdown()

        if config.USE_NGROK:
            from pyngrok import ngrok
            ngrok.disconnect(config.BASE_URL)
    except Exception as e:
        logger.exception(e)
