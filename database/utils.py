from collections import UserDict
from datetime import datetime


def dt_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        return obj.strftime("%d.%m.%Y")
    elif isinstance(obj, UserDict):
        return obj.data
    raise TypeError("Type %s not serializable" % type(obj))
