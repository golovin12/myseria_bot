from bots import MySeriaBot, ZetflixBot, AdminBot
from config import settings
from consts import MySeria, Zetflix, ADMIN_KEY


def init_bots():
    settings.user_bots[ADMIN_KEY] = AdminBot(
        bot_token=settings.ADMIN_BOT_TOKEN,
        redis_host=None,
        skip_updates=settings.SKIP_UPDATES,
        key=ADMIN_KEY)
    settings.user_bots[MySeria.KEY] = MySeriaBot(
        bot_token=settings.MY_SERIA_BOT_TOKEN,
        redis_host=settings.REDIS_HOST,
        skip_updates=settings.SKIP_UPDATES,
        key=MySeria.KEY)
    settings.user_bots[Zetflix.KEY] = ZetflixBot(
        bot_token=settings.ZETFLIX_BOT_TOKEN,
        redis_host=settings.REDIS_HOST,
        skip_updates=settings.SKIP_UPDATES,
        key=Zetflix.KEY)
