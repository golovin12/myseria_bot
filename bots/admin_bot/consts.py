class ControlCommand:
    NEW_ADDR = "#new_addr: https?://.*"
    SHOW_ADMINS = "#show_admins"
    CREATE_ADMIN = r"#create_admin: \d*"
    DELETE_ADMIN = r"#delete_admin: \d*"
    HELP = "/help"

    choices = (
        (NEW_ADDR, "Установить новый адрес для сайта MySeria"),
        (SHOW_ADMINS, "Получить список id админов"),
        (CREATE_ADMIN, "Добавить администратора"),
        (DELETE_ADMIN, "Удалить админа"),
        (HELP, "Доступные команды"),
    )

    all_commands = "\n".join(f"{command} - {name}" for command, name in choices)
