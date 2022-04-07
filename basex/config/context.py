__author__ = 'ziyan.yin'
__describe__ = ''

from contextvars import ContextVar, Token
from typing import Any, TypeVar, Generic

T = TypeVar('T', bound=Any)


class ContextWrapper(Generic[T]):

    def __init__(self, name: str, default=None):
        self._value: ContextVar = ContextVar(name, default=default)

    @property
    def value(self) -> T:
        return self._value.get()

    def set(self, value: T) -> Token[T]:
        return self._value.set(value)

    def reset(self, token: Token):
        self._value.reset(token)
