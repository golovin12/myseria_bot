import logging

from config import settings
from database.models import Admin
from serial_services.my_seria import MySeriaService
from serial_services.zetflix import ZetflixService

logger = logging.getLogger(__name__)


async def startup() -> None:
    if settings.ADMIN_ID:
        # добавляем администратора
        admin_id = int(settings.ADMIN_ID)
        await Admin(admin_id, is_admin=True).save()
        logger.info(f"Добавлен администратор с id {admin_id}? -> {(await Admin.get_object(admin_id)).is_admin}")
    if settings.VK_ACCESS_TOKEN:
        # обновляем адрес my_seria
        my_seria_url_is_update = await MySeriaService.update_url_by_vk(settings.VK_ACCESS_TOKEN)
        logger.info(f"Адрес MySeria обновлен? -> {my_seria_url_is_update}")
        # обновляем адрес zetflix
        zetflix_url_is_update = await ZetflixService.update_url_by_vk(settings.VK_ACCESS_TOKEN)
        logger.info(f"Адрес Zetflix обновлен? -> {zetflix_url_is_update}")
    if settings.USE_NGROK:
        # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
        from pyngrok import ngrok
        port = str(settings.PORT)
        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(f"{settings.HOST}:{port}").public_url
        logger.info("ngrok tunnel \"{}\" -> \"http://{}:{}\"".format(public_url, settings.HOST, port))

        # webhooks to use the public ngrok URL
        settings.PUBLIC_URL = public_url

    for bot in settings.user_bots.values():
        await bot.on_startapp(settings.PUBLIC_URL, settings.SECRET_TOKEN, settings.SSL_PUBLIC_PATH)
