__author__ = 'ziyan.yin'

from typing import Any, Optional, Collection


def is_empty(arg: Any) -> bool:
    """
        check if object is none or empty
            >>> obj = ''
            >>> is_empty(obj)
            True
    """
    if arg is None:
        return True
    if isinstance(arg, str) and not arg:
        return True
    if isinstance(arg, Collection) and not arg:
        return True
    return False


def default_if_null(arg: Any, default: Optional[Any] = None) -> Any:
    """
        get obj if not none else default data
            >>> default_if_null(None, [])
            []
            >>> default_if_null('a', [])
            'a'
    """
    return arg if not is_empty(arg) else default


def equals(arg1: Any, arg2: Any) -> bool:
    """
        check if two object equal
            >>> equals('a', 'b')
            False
    """
    if arg1 == arg2:
        return True
    if (arg1 is None) or (arg2 is None):
        return False
    return arg1.__eq__(arg2)
