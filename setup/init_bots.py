from bots.admin_bot import AdminBot
from bots.my_seria_bot import MySeriaBot
from bots.zetflix_bot import ZetflixBot
from config import settings
from consts import MySeria, Zetflix, ADMIN_KEY


def init_bots():
    settings.user_bots[ADMIN_KEY] = AdminBot(
        name='admin',
        bot_token=settings.ADMIN_BOT_TOKEN,
        redis_host=None,
        skip_updates=settings.SKIP_UPDATES,
        key=ADMIN_KEY)
    settings.user_bots[MySeria.KEY] = MySeriaBot(
        name='my_seria',
        bot_token=settings.MY_SERIA_BOT_TOKEN,
        redis_host=settings.REDIS_HOST,
        skip_updates=settings.SKIP_UPDATES,
        key=MySeria.KEY)
    settings.user_bots[Zetflix.KEY] = ZetflixBot(
        name='zetflix',
        bot_token=settings.ZETFLIX_BOT_TOKEN,
        redis_host=settings.REDIS_HOST,
        skip_updates=settings.SKIP_UPDATES,
        key=Zetflix.KEY)
