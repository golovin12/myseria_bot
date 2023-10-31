import config
from bots import MySeriaBot, ZetflixBot, AdminBot
from consts import MySeria, Zetflix, ADMIN_KEY


def init_bots():
    config.user_bots[ADMIN_KEY] = AdminBot(
        bot_token=config.ADMIN_BOT_TOKEN,
        redis_host=None,
        skip_updates=config.SKIP_UPDATES,
        key=ADMIN_KEY)
    config.user_bots[MySeria.KEY] = MySeriaBot(
        bot_token=config.MY_SERIA_BOT_TOKEN,
        redis_host=config.REDIS_HOST,
        skip_updates=config.SKIP_UPDATES,
        key=MySeria.KEY)
    config.user_bots[Zetflix.KEY] = ZetflixBot(
        bot_token=config.ZETFLIX_BOT_TOKEN,
        redis_host=config.REDIS_HOST,
        skip_updates=config.SKIP_UPDATES,
        key=Zetflix.KEY)
