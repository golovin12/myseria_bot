PAGINATION_SERIALS_PREFIX = "#page-serials:"


class ControlCommand:
    ADD_SERIALS = "add_serials"
    CANCEL = "cancel"
    DELETE_SERIALS = "delete_serials"
    HELP = "help"
    MY_SERIALS = "my_serials"
    REBOOT = "reboot"
    NEW_SERIES = "new_series"
    START = "start"

    choices = (
        (START, "Приветствие"),
        (HELP, "Помощь"),
        (ADD_SERIALS, "Добавить сериалы для отслеживания"),
        (DELETE_SERIALS, "Удалить сериалы из отслеживания"),
        (NEW_SERIES, "Получить информацию о новых сериях"),
        (MY_SERIALS, "Получить информацию об отслеживаемых сериалах"),
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
