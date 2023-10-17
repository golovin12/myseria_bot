MY_SERIA_KEY = 'my_seria_url'  # Ключ для получения url к сайту MySeria


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
        (MY_SERIALS, "Получить информацию об отслеживаемых сериалах"),
        (NEW_SERIES, "Получить информацию о новых сериях"),
        (CANCEL, "Отменить команду"),
        (REBOOT, "Очистить список отслеживаемых сериалов"),
    )

    all_commands = "\n".join(f"/{command} - {name}" for command, name in choices)
