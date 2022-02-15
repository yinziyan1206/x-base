__author__ = 'ziyan.yin'

import datetime
import string

import cython


@cython.infer_types(True)
def is_empty(arg: str) -> bool:
    """
        string is None or ''
            >>> is_empty('a')
            False
    """
    if arg is None:
        return True
    if str(arg).strip() == '':
        return True
    return False


@cython.infer_types(True)
def is_number(arg: str) -> bool:
    """
        string is number like 1.0, -1
            >>> is_number('1.5')
            True
    """
    if len(arg) > 1 and arg[0] == '0':
        return False
    if arg.startswith('-'):
        arg = arg[1:]
    if arg.isdigit():
        return True
    if arg.find('.') > 0:
        args = arg.split('.')
        if len(args) > 0 and args[0].isdigit() and args[1].isdigit():
            return True
    return False


@cython.infer_types(True)
def is_digit(arg: str) -> bool:
    """
        isdigit() method
    """
    return arg.isdigit()


@cython.infer_types(True)
def is_bool(arg: str) -> bool:
    """
        check if string is true or false
            >>> is_bool('true')
            True
    """
    if arg in ('true', 'false'):
        return True
    return False


@cython.infer_types(True)
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


@cython.infer_types(True)
def is_chinese(arg: str) -> bool:
    """
        check if string is utf-8 chinese
            >>> is_chinese('我')
            True
    """
    for ch in arg:
        if '\u4e00' <= ch <= '\u9fa5':
            return True
    return False


@cython.infer_types(True)
def is_letter(arg: str) -> bool:
    """
        check if string is number or words
            >>> is_letter('ab12123')
            True
    """
    for ch in arg:
        if ch not in frozenset(string.ascii_letters + string.digits):
            return False
    return True


@cython.infer_types(True)
def is_tag(arg: str) -> bool:
    """
        check if string is tag format
            >>> is_tag('Abc_1234')
            True
    """
    for ch in arg:
        if ch not in frozenset(string.ascii_letters + string.digits + '_'):
            return False
    return True


@cython.infer_types(True)
def is_label(arg: str) -> bool:
    """
        check if string is sql column format
            >>> is_label('ab12123')
            True
    """
    if len(arg) > 0 and arg[0] in frozenset(string.digits):
        return False
    for ch in arg:
        if ch not in set(string.ascii_letters + string.digits + '_'):
            return False
    return True


@cython.infer_types(True)
def is_legal(arg: str) -> bool:
    """
        check if string has illegal word
            >>> is_legal('ab12123')
            True
    """
    illegal_signal = frozenset('~|')
    for ch in arg:
        if ch in illegal_signal:
            return False
    return True
