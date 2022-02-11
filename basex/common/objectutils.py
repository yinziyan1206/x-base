__author__ = 'ziyan.yin'

from typing import Any


def is_empty(arg: Any) -> bool:
    """
        check if object is none or empty
            >>> obj = ''
            >>> is_empty(obj)
    """
    if arg is None:
        return True
    if isinstance(arg, str) and arg.strip() == "":
        return True
    if isinstance(arg, list) and len(arg) < 1:
        return True
    if isinstance(arg, dict) and len(arg.keys()) < 1:
        return True
    return False


def default_if_null(arg: Any, default='') -> Any:
    """
        get obj if not none else default data
            >>> default_if_null(None, [])
        return []
            >>> default_if_null('a', [])
        return 'a'
    """
    return arg if arg is not None else default


def first_not_null(*args) -> Any:
    """
        get list obj first not-null object
            >>> first_not_null(None, 'a', 'b')
        return 'a'
    """
    if args is not None:
        for arg in args:
            if arg is not None:
                return arg
    return None


def all_not_null(*args) -> bool:
    """
        check if all in list is not none
            >>> all_not_null('a', None)
        return False
    """
    if args is not None:
        for arg in args:
            if arg is None:
                return False
        return True
    return False


def equals(arg1, arg2) -> bool:
    """
        check if two object equal
            >>> equals('a', 'b')
    """
    if arg1 == arg2:
        return True
    if (arg1 is None) or (arg2 is None):
        return False
    return arg1.__eq__(arg2)


