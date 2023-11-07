import abc
import re
from collections import UserDict
from typing import Any


class ValidateField(abc.ABC):
    def __init__(self, is_pk: bool = False):
        self.is_pk = is_pk

    def __set_name__(self, owner, name):
        self.field_name = name

    def __set__(self, instance, value):
        if self.is_pk and self.field_name in instance.__dict__:
            # Для primary_keys позволяем создать атрибут со значением по умолчанию, но не даём его изменять
            raise AttributeError(f"property '{self.field_name}' not changeable")
        value = self.validate(self.field_name, value)
        instance.__dict__[self.field_name] = value

    @abc.abstractmethod
    def validate(self, name, value):
        """Возвращает проверенное значение или возбуждает ValueError"""


class CharField(ValidateField):
    def __init__(self, empty_allowed: bool = True, is_pk: bool = False):
        super().__init__(is_pk)
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
            if re.fullmatch(r"^https?://[0-9A-z.]+(\.[0-9A-z.])?(\.[a-z])?$", value):
                return value
        raise ValueError(f'{name} must be url address without path')


class PositiveIntegerField(ValidateField):
    def validate(self, name: str, value: Any) -> int:
        if isinstance(value, int) and value >= 0:
            return value
        raise ValueError(f'{name} must be positive int')


class BooleanField(ValidateField):
    def validate(self, name: str, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        raise ValueError(f'{name} must be bool')


class JsonField(ValidateField):
    def __init__(self, user_type: UserDict | None = None, is_pk: bool = False):
        super().__init__(is_pk)
        if user_type is not None and not issubclass(user_type, UserDict):
            raise ValueError('user_dict must be subclass UserDict')
        self.user_type = user_type

    def validate(self, name: str, value: Any) -> UserDict | dict:
        if isinstance(value, dict | UserDict):
            return self.user_type(value) if self.user_type else value
        raise ValueError(f'{name} must be {self.user_type or "dict"}')
