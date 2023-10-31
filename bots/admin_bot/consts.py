class ControlCommand:
    NEW_MY_SERIA_ADDR = "#new_my_seria_addr: https?://.*"
    NEW_ZETFLIX_ADDR = "#new_zetflix_addr: https?://.*"
    SHOW_ADMINS = "#show_admins"
    CREATE_ADMIN = r"#create_admin: \d*"
    DELETE_ADMIN = r"#delete_admin: \d*"
    HELP = "/help"

    choices = (
        (NEW_MY_SERIA_ADDR, "Установить новый адрес для сайта MySeria"),
        (NEW_ZETFLIX_ADDR, "Установить новый адрес для сайта Zetflix"),
        (SHOW_ADMINS, "Получить список id админов"),
        (CREATE_ADMIN, "Добавить администратора"),
        (DELETE_ADMIN, "Удалить админа"),
        (HELP, "Доступные команды"),
    )

    all_commands = "\n".join(f"{command} - {name}" for command, name in choices)
