from bots.admin_bot import AdminBot
from bots.my_seria_bot import MySeriaBot
from bots.zetflix_bot import ZetflixBot
from config import settings
from consts import MySeria, Zetflix, ADMIN_KEY


def init_bots():
    admin_bot_name = ADMIN_KEY
    my_seria_bot_name = MySeria.KEY
    zetflix_bot_name = Zetflix.KEY
    settings.user_bots[admin_bot_name] = AdminBot(
        name=admin_bot_name,
        bot_token=settings.ADMIN_BOT_TOKEN,
        redis_host=None,
        skip_updates=settings.SKIP_UPDATES,
    )
    settings.user_bots[my_seria_bot_name] = MySeriaBot(
        name=my_seria_bot_name,
        bot_token=settings.MY_SERIA_BOT_TOKEN,
        redis_host=settings.REDIS_HOST,
        skip_updates=settings.SKIP_UPDATES,
    )
    settings.user_bots[zetflix_bot_name] = ZetflixBot(
        name=zetflix_bot_name,
        bot_token=settings.ZETFLIX_BOT_TOKEN,
        redis_host=settings.REDIS_HOST,
        skip_updates=settings.SKIP_UPDATES,
    )
