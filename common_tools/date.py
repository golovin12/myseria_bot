import re
from datetime import datetime

MONTH_NAMES_RU = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8, "сентября": 9,
    "октября": 10, "ноября": 11, "декабря": 12,
}


def get_date_by_localize_string(date_string: str) -> datetime:
    """Формирует дату из строки вида: %d %B %Y для русского языка"""
    if not isinstance(date_string, str):
        raise TypeError(f'date_string must be str not {type(date_string)}')
    date_string = date_string.lower()
    if re.fullmatch(r'\d+ [а-я]+ \d+', date_string):
        day, month_name, year = date_string.split()
        if month_name in MONTH_NAMES_RU:
            month_num = MONTH_NAMES_RU[month_name]
            return datetime(day=int(day), month=month_num, year=int(year))
    raise ValueError('date_string does not math format %d %B %Y')
