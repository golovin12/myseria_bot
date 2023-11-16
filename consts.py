ADMIN_KEY = "admin"

LIMIT_SEARCH_DEPTH = 120


class RedisDatabases:
    default = 1  # хранилище для данных
    fsm_storage = 2  # хранилище для fsm
    test = 9   # хранилище для тестов


class MySeria:
    KEY = 'my_seria'
    VK_GROUP_ID = 200719078  # идентификатор ВК группы сайта с сериалами


class Zetflix:
    KEY = 'zetflix'
    VK_GROUP_ID = 199158228
