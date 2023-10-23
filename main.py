import logging

from fastapi import FastAPI

import api
import bots
import config
from consts import MY_SERIA_ROUTE, ADMIN_ROUTE, SKIP_UPDATES
from database.models import User

logger = logging.getLogger('uvicorn')


async def shutdown() -> None:
    try:
        await config.aioredis.aclose()

        await config.my_seria_bot.delete_webhook(SKIP_UPDATES)
        await config.admin_bot.delete_webhook(SKIP_UPDATES)

        await config.my_seria_dp.storage.close()
        await config.admin_dp.storage.close()

        if config.USE_NGROK:
            from pyngrok import ngrok
            ngrok.disconnect(config.BASE_URL)
        logger.info('shutdown is complete')
    except Exception as e:
        logger.info('shutdown_error:', e)


async def startup() -> None:
    if config.ADMIN_ID:
        admin_id = int(config.ADMIN_ID)
        await User(admin_id).set_is_admin()
        logger.info(f"Добавлен администратор с id {admin_id}? -> {await User(admin_id).is_admin()}")
    if config.VK_ACCESS_TOKEN:
        my_seria_url_is_update = await bots.update_my_seria_url_by_vk(config.VK_ACCESS_TOKEN)
        logger.info(f"Адрес сайта обновлен? -> {my_seria_url_is_update}")
    if config.USE_NGROK:
        # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
        from pyngrok import ngrok
        port = str(config.PORT)
        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(f"{config.HOST}:{port}").public_url
        logger.info("ngrok tunnel \"{}\" -> \"http://{}:{}\"".format(public_url, config.HOST, port))

        # Update any base URLs or webhooks to use the public ngrok URL
        config.BASE_URL = public_url

    await config.my_seria_bot.set_webhook(f"{config.BASE_URL}/bot{MY_SERIA_ROUTE}", secret_token=config.SECRET_TOKEN,
                                          drop_pending_updates=SKIP_UPDATES)

    await config.my_seria_bot.set_my_commands(bots.my_seria_menu_commands)
    config.my_seria_dp.include_routers(bots.my_seria_router)

    await config.admin_bot.set_webhook(f"{config.BASE_URL}/bot{ADMIN_ROUTE}", secret_token=config.SECRET_TOKEN,
                                       drop_pending_updates=SKIP_UPDATES)
    config.admin_dp.include_routers(bots.admin_router)
    logger.info('startup is complete')


app = FastAPI()
app.include_router(api.router)
app.add_event_handler('startup', startup)
app.add_event_handler('shutdown', shutdown)
