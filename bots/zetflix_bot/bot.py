from bots.base_user_bot import UserBot, UserController
from serial_services.my_seria import MySeriaService


class ZetflixUserController(UserController):
    serial_service_class = MySeriaService  # todo ZetflixService


class ZetflixBot(UserBot):
    controller = ZetflixUserController
