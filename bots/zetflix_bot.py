from bots.base_user_bot import UserBot, UserController
from serial_services.zetflix import ZetflixService


class ZetflixUserController(UserController):
    serial_service_class = ZetflixService


class ZetflixBot(UserBot):
    controller = ZetflixUserController
