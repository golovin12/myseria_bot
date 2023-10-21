import logging

from fastapi import FastAPI

import api
import bots
from consts import MY_SERIA_ROUTE, ADMIN_ROUTE, SKIP_UPDATES
import config

logger = logging.getLogger(__name__)


async def shutdown():
    try:
        await config.aioredis.aclose()

        await config.my_seria_bot.delete_webhook(SKIP_UPDATES)
        await config.admin_bot.delete_webhook(SKIP_UPDATES)

        await config.my_seria_dp.storage.close()
        await config.admin_dp.storage.close()
        print('shutdown')
    except Exception as e:
        print('shutdown_error:', e)


async def startup():
    if config.USE_NGROK:
        # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
        from pyngrok import ngrok
        port = str(config.PORT)
        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port).public_url
        logger.info("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

        # Update any base URLs or webhooks to use the public ngrok URL
        config.BASE_URL = public_url

    await config.my_seria_bot.set_webhook(f"{config.BASE_URL}/bot{MY_SERIA_ROUTE}", secret_token=config.SECRET_TOKEN,
                                          drop_pending_updates=SKIP_UPDATES)

    await config.my_seria_bot.set_my_commands(bots.my_seria_menu_commands)
    config.my_seria_dp.include_routers(bots.my_seria_router)

    await config.admin_bot.set_webhook(f"{config.BASE_URL}/bot{ADMIN_ROUTE}", secret_token=config.SECRET_TOKEN,
                                       drop_pending_updates=SKIP_UPDATES)
    config.admin_dp.include_routers(bots.admin_router)
    print('startup')


app = FastAPI()
app.include_router(api.router)
app.add_event_handler('startup', startup)
app.add_event_handler('shutdown', shutdown)
