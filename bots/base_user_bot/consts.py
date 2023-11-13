PAGINATION_SERIALS_PREFIX = "#page-serials:"


class ControlCommand:
    START = "start"
    HELP = "help"
    ADD_SERIAL = "add_serial"
    DELETE_SERIAL = "delete_serial"
    NEW_SERIES = "get_new_series"
    SERIAL_INFO = "get_serial_info"
    CANCEL = "cancel"
    REBOOT = "reboot"
    ACTUAL_URL = "get_actual_url"

    choices = (
        (START, "Приветствие"),
        (HELP, "Помощь"),
        (ADD_SERIAL, "Добавить сериалы для отслеживания"),
        (DELETE_SERIAL, "Удалить сериалы из отслеживания"),
        (NEW_SERIES, "Получить информацию о новых сериях"),
        (SERIAL_INFO, "Получить информацию об отслеживаемых сериалах"),
        (CANCEL, "Отменить команду"),
        (REBOOT, "Очистить список отслеживаемых сериалов"),
        (ACTUAL_URL, "Получить актуальный адрес сайта"),
    )

    all_commands = "\n".join(f"/{command} - {name}" for command, name in choices)


class CallbackButtonInfo:
    CLOSE = '__exit__'
    ALL = '__all__'

    method_name = {
        CLOSE: 'Закрыть',
        ALL: 'Все новые серии',
    }
