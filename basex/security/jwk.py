__author__ = 'ziyan.yin'
__describe__ = 'jws native'

import hashlib
import hmac

from .exceptions import JWKError

HASHES = {
    'HS256': hashlib.sha256,
    'HS384': hashlib.sha384,
    'HS512': hashlib.sha512
}


class HMACKey:

    def __init__(self, key: bytes, algorithm: str):
        self._hash_alg = HASHES.get(algorithm)
        invalid_strings = (
            b"-----BEGIN PUBLIC KEY-----",
            b"-----BEGIN RSA PUBLIC KEY-----",
            b"-----BEGIN CERTIFICATE-----",
            b"ssh-rsa",
        )
        if any(string_value in key for string_value in invalid_strings):
            raise JWKError(
                "The specified key is an asymmetric key or x509 certificate and"
                " should not be used as an HMAC secret."
            )
        self.prepared_key = key

    def sign(self, msg):
        return hmac.new(self.prepared_key, msg, self._hash_alg).digest()

    def verify(self, msg, sig):
        return hmac.compare_digest(sig, self.sign(msg))
