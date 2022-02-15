__author__ = 'ziyan.yin'

from typing import Any

import cython


@cython.infer_types(True)
def is_empty(arg: Any) -> bool:
    """
        check if object is none or empty
            >>> obj = ''
            >>> is_empty(obj)
            True
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


@cython.infer_types(True)
def default_if_null(arg: Any, default: Any=None) -> Any:
    """
        get obj if not none else default data
            >>> default_if_null(None, [])
            []
            >>> default_if_null('a', [])
            'a'
    """
    return arg if arg is not None else default


@cython.infer_types(True)
def first_not_null(*args: Any) -> Any:
    """
        get list obj first not-null object
            >>> first_not_null(None, 'a', 'b')
            'a'
    """
    if args is not None:
        for arg in args:
            if arg is not None:
                return arg
    return None


@cython.infer_types(True)
def all_not_null(*args: Any) -> bool:
    """
        check if all in list is not none
            >>> all_not_null('a', None)
            False
    """
    if args is not None:
        for arg in args:
            if arg is None:
                return False
        return True
    return False


@cython.infer_types(True)
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


