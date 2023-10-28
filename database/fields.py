import abc
import re
from datetime import datetime
from typing import Any, Collection


class ValidateField(abc.ABC):
    def __set_name__(self, owner, name):
        self.field_name = name

    def __set__(self, instance, value):
        value = self.validate(self.field_name, value)
        instance.__dict__[self.field_name] = value

    @abc.abstractmethod
    def validate(self, name, value):
        """Возвращает проверенное значение или возбуждает ValueError"""


class CharField(ValidateField):
    def __init__(self, empty_allowed: bool = True):
        self.empty_allowed = empty_allowed

    def validate(self, name: str, value: Any) -> str:
        if isinstance(value, str):
            value = value.strip()
            if not self.empty_allowed and not value:
                raise ValueError(f'{name} cannot be empty str!')
            return value
        raise ValueError(f'{name} must be str!')


class UrlField(ValidateField):
    def validate(self, name, value):
        if isinstance(value, str):
            value = value.strip().removesuffix('/')
            if re.fullmatch(r"^https?://[0-9A-z.]+.[0-9A-z.]+.[a-z]+$", value):
                return value
        raise ValueError(f'{name} must be url address')


class IntegerField(ValidateField):
    def validate(self, name: str, value: Any) -> int:
        if isinstance(value, int):
            return value
        raise ValueError(f'{name} must be int')


class BooleanField(ValidateField):
    def validate(self, name: str, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        raise ValueError(f'{name} must be int')


class DateField(ValidateField):
    def validate(self, name: str, value: Any) -> datetime:
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%d.%m.%Y')
            except ValueError:
                raise ValueError(f'{name} must be stringformat %d.%m.%Y')
        elif isinstance(value, datetime):
            return value
        raise ValueError(f'{name} must be datetime or stringformat %d.%m.%Y')


class JsonField(ValidateField):
    def __init__(self, user_type=None):
        self.user_type = user_type

    def validate(self, name: str, value: Any) -> Collection[Any]:
        if self.user_type is not None:
            return self.user_type(value)
        elif isinstance(value, dict):
            return value
        raise ValueError(f'{name} must be {self.user_type or "dict"}')
