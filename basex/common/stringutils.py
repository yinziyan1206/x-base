__author__ = 'ziyan.yin'

import datetime
from typing import Optional

from ..native import native_utils


def is_empty(arg: Optional[str]) -> bool:
    """
        string is None or ''
            >>> is_empty('a')
            False
    """
    if arg is None:
        return True
    if arg == '':
        return True
    return False


def is_blank(arg: Optional[str]) -> bool:
    if arg is None:
        return False
    return native_utils.check_blank(arg.encode())


def is_number(arg: str) -> bool:
    """
        string is number like 1.0, -1
            >>> is_number('1.5')
            True
    """
    if arg is None:
        return False
    return native_utils.check_number(arg.encode())


def is_digit(arg: str) -> bool:
    """
        isdigit() method
    """
    if arg is None:
        return False
    return arg.isdigit()


def is_bool(arg: str) -> bool:
    """
        check if string is true or false
            >>> is_bool('true')
            True
    """
    if arg is None:
        return False
    if arg == 'true' or arg == 'false':
        return True
    return False


def is_date(arg: str, base='%Y-%m-%d %H:%M:%S') -> bool:
    """
        check if string is date-format
            >>> is_date('2020-01-01 00:00:00')
            True
    """
    try:
        datetime.datetime.strptime(arg, base)
        return True
    except (TypeError, ValueError):
        return False


def is_chinese(arg: str) -> bool:
    """
        check if string is utf-8 chinese
            >>> is_chinese('我')
            True
    """
    if arg is None:
        return False
    return native_utils.check_chinese(arg.encode())


def is_letter(arg: str) -> bool:
    """
        check if string is number or words
            >>> is_letter('ab12123')
            True
    """
    if arg is None:
        return False
    return native_utils.check_letter(arg.encode())


def is_alpha(arg: str) -> bool:
    """
        check if string is alpha
            >>> is_alpha('ababc')
            True
    """
    if arg is None:
        return False
    return native_utils.check_alpha(arg.encode())


def is_title(arg: str) -> bool:
    """
        check if string is tag format
            >>> is_title('Abc_1234')
            True
    """
    if arg is None:
        return False
    return native_utils.check_title(arg.encode())
