from datetime import datetime

MONTH_NAMES_RU = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8, "сентября": 9,
    "октября": 10, "ноября": 11, "декабря": 12,
}


def get_date_by_localize_date_string(date_string: str) -> datetime:
    """Формирует дату из строки вида: 29 сентября 2019"""
    day, month, year = date_string.split()
    month_num = MONTH_NAMES_RU[month]
    return datetime(day=int(day), month=month_num, year=int(year))
