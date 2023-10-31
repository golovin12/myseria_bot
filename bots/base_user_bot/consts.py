PAGINATION_SERIALS_PREFIX = "#page-serials:"


class ControlCommand:
    ADD_SERIAL = "add_serial"
    CANCEL = "cancel"
    DELETE_SERIAL = "delete_serial"
    HELP = "help"
    SERIAL_INFO = "serial_info"
    REBOOT = "reboot"
    NEW_SERIES = "new_series"
    START = "start"

    choices = (
        (START, "Приветствие"),
        (HELP, "Помощь"),
        (ADD_SERIAL, "Добавить сериалы для отслеживания"),
        (DELETE_SERIAL, "Удалить сериалы из отслеживания"),
        (NEW_SERIES, "Получить информацию о новых сериях"),
        (SERIAL_INFO, "Получить информацию об отслеживаемых сериалах"),
        (CANCEL, "Отменить команду"),
        (REBOOT, "Очистить список отслеживаемых сериалов"),
    )

    all_commands = "\n".join(f"/{command} - {name}" for command, name in choices)


class CallbackButtonInfo:
    CLOSE = '__exit__'
    ALL = '__all__'

    method_name = {
        CLOSE: 'Закрыть',
        ALL: 'Все новые серии',
    }
