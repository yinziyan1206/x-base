__author__ = 'ziyan.yin'

import datetime
from typing import Optional

from ..native import utils


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


def is_number(arg: str) -> bool:
    """
        string is number like 1.0, -1
            >>> is_number('1.5')
            True
    """
    return utils.check_number(arg)


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
        return True
    return utils.check_chinese(arg.encode())


def is_letter(arg: str) -> bool:
    """
        check if string is number or words
            >>> is_letter('ab12123')
            True
    """
    return utils.check_letter(arg)
