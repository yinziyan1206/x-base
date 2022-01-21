#!/usr/bin/env python
__author__ = 'ziyan.yin'

import hashlib
import hmac
import base64
from typing import Union


def md5(content: Union[str, bytes, bytearray, memoryview]) -> str:
    """
    md5 encrypt

    :param content: words
    :return: encrypted codes
    """
    m = hashlib.md5()
    if isinstance(content, str):
        content = content.encode()
    m.update(content)
    return m.hexdigest()


def hmac_md5(content: Union[str, bytes, bytearray, memoryview], key: bytes = b'') -> str:
    """
    md5 encrypt with hmac

    :param content: words
    :param key: secret
    :return: encrypted words
    """
    if isinstance(content, str):
        content = content.encode()
    m = hmac.new(key, content, digestmod=hashlib.md5)
    return m.hexdigest()


def sha1(content: Union[str, bytes, bytearray, memoryview]) -> str:
    """
    sha1 encrypt

    :param content: words
    :return: encrypted codes
    """
    sha = hashlib.sha1()
    if isinstance(content, str):
        content = content.encode()
    sha.update(content)
    return sha.hexdigest()


def hmac_sha1(content: Union[str, bytes, bytearray, memoryview], key: bytes = b'') -> str:
    """
    sha1 encrypt with hmac

    :param content: words
    :param key: secret
    :return: encrypted words
    """
    if isinstance(content, str):
        content = content.encode()
    m = hmac.new(key, content, digestmod=hashlib.sha1)
    return m.hexdigest()


def sha256(content: Union[str, bytes, bytearray, memoryview]) -> str:
    """
    sha256 encrypt

    :param content: words
    :return: encrypted codes
    """
    sha = hashlib.sha256()
    if isinstance(content, str):
        content = content.encode()
    sha.update(content)
    return sha.hexdigest()


def hmac_sha256(content: Union[str, bytes, bytearray, memoryview], key: bytes = b'') -> str:
    """
    sha256 encrypt with hmac

    :param content: words
    :param key: secret
    :return: encrypted words
    """
    if isinstance(content, str):
        content = content.encode()
    m = hmac.new(key, content, digestmod=hashlib.sha256)
    return m.hexdigest()


def b64encode(content: Union[str, bytes, bytearray, memoryview]) -> bytes:
    """
    base64 encode

    :param content: words
    :return: encrypted codes
    """
    if isinstance(content, str):
        content = content.encode()
    return base64.b64encode(content)


def b64decode(content: Union[str, bytes, bytearray, memoryview]) -> bytes:
    """
    base64 decode

    :param content: codes
    :return: decrypted words
    """
    if isinstance(content, str):
        content = content.encode()
    return base64.b64decode(content)
