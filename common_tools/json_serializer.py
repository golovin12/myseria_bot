from collections import UserDict
from datetime import datetime, date
from typing import Any


def dict_date_serializer(obj: Any) -> Any:
    """
    JSON serializer

    datetime|date -> "%d.%m.%Y"

    UserDict -> dict
    """
    if isinstance(obj, datetime | date):
        return obj.strftime("%d.%m.%Y")
    elif isinstance(obj, UserDict):
        return obj.data
    raise TypeError("Type %s not serializable" % type(obj))
