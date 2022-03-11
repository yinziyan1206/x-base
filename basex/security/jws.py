__author__ = 'ziyan.yin'
__describe__ = 'jwt tools'

import binascii
from typing import Mapping

import orjson

from .exceptions import JWSSignatureError, JWSError
from .jwk import HMACKey
from ..common import cryptutils


def verify(signing_input, signature, key, algorithm):
    if not HMACKey(key.encode(), algorithm).verify(signing_input, signature):
        raise JWSSignatureError()


def sign(data, key, algorithm):
    return HMACKey(key.encode(), algorithm).sign(data)


def load(token):
    if isinstance(token, str):
        token = token.encode("utf-8")
    try:
        signing_input, crypto_segment = token.rsplit(b".", 1)
        header_segment, claims_segment = signing_input.split(b".", 1)
        header_data = b64decode(header_segment)
    except ValueError:
        raise JWSError("Not enough segments")
    except TypeError:
        raise JWSError("Invalid header padding")

    try:
        header = orjson.loads(header_data.decode("utf-8"))
    except ValueError as e:
        raise JWSError("Invalid header string: %s" % e)

    if not isinstance(header, Mapping):
        raise JWSError("Invalid header string: must be a json object")

    try:
        payload = b64decode(claims_segment)
    except (TypeError, binascii.Error):
        raise JWSError("Invalid payload padding")

    try:
        signature = b64decode(crypto_segment)
    except (TypeError, binascii.Error):
        raise JWSError("Invalid crypto padding")

    return header, payload, signing_input, signature


def b64decode(content):
    rem = len(content) % 4
    if rem > 0:
        content += b"=" * (4 - rem)
    return cryptutils.urlsafe_b64decode(content)


def b64encode(content):
    return cryptutils.urlsafe_b64encode(content).replace(b"=", b"")
