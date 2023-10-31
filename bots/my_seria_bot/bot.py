from bots.base_user_bot import UserBot, UserController
from serial_services.my_seria import MySeriaService


class MySeriaUserController(UserController):
    serial_service_class = MySeriaService


class MySeriaBot(UserBot):
    controller = MySeriaUserController
