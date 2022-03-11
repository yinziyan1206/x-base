__author__ = 'ziyan.yin'
__describe__ = 'exception'


class JWTError(Exception):
    pass


class JWSError(JWTError):
    pass


class JWSSignatureError(JWTError):
    pass


class JWKError(JWTError):
    pass


class JWTClaimsError(JWTError):
    pass


class ExpiredSignatureError(JWTError):
    pass
