import logging

import config
from database.models import Admin
from serial_services.my_seria import MySeriaService
from serial_services.zetflix import ZetflixService

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console)


async def startup() -> None:
    if config.ADMIN_ID:
        # добавляем администратора
        admin_id = int(config.ADMIN_ID)
        await Admin(admin_id, is_admin=True).save()
        logger.info(f"Добавлен администратор с id {admin_id}? -> {(await Admin.get_object(admin_id)).is_admin}")
    if config.VK_ACCESS_TOKEN:
        # обновляем адрес my_seria
        my_seria_url_is_update = await MySeriaService.update_url_by_vk(config.VK_ACCESS_TOKEN)
        logger.info(f"Адрес MySeria обновлен? -> {my_seria_url_is_update}")
        # обновляем адрес zetflix
        zetflix_url_is_update = await ZetflixService.update_url_by_vk(config.VK_ACCESS_TOKEN)
        logger.info(f"Адрес Zetflix обновлен? -> {zetflix_url_is_update}")
    if config.USE_NGROK:
        # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
        from pyngrok import ngrok
        port = str(config.PORT)
        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(f"{config.HOST}:{port}").public_url
        logger.info("ngrok tunnel \"{}\" -> \"http://{}:{}\"".format(public_url, config.HOST, port))

        # Update any base URLs or webhooks to use the public ngrok URL
        config.BASE_URL = public_url

    for bot in config.user_bots.values():
        await bot.on_startapp(config.BASE_URL, config.SECRET_TOKEN)
