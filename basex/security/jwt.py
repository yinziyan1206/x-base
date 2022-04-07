__author__ = 'ziyan.yin'
__describe__ = ''

from calendar import timegm
from datetime import datetime
from typing import Mapping

import orjson

from . import jwk
from .exceptions import JWTError, JWTClaimsError, ExpiredSignatureError
from .jws import verify, sign, load, b64decode, b64encode


def encode(claims: dict, key: str, algorithm='HS256', headers=None, access_token=None) -> str:
    """
    JWTs are JWS signed objects with a few reserved claims.

    Args:
        claims (dict): A claims set to sign
        key (str): The key to use for signing the claim set
        algorithm (str, optional): The algorithm to use for signing the
            the claims.  Defaults to HS256.
        headers (dict, optional): A set of headers that will be added to
            the default headers.  Any headers that are added as additional
            headers will override the default headers.
        access_token (str, optional): If present, the 'at_hash' claim will
            be calculated and added to the claims present in the 'claims'
            parameter.

    Returns:
        str: The string representation of the header, claims, and signature.

    Raises:
        JWTError: If there is an error encoding the claims.

    Examples:

        >>> jwt.encode({'a': 'b'}, 'secret', algorithm='HS256')
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhIjoiYiJ9.jiMyrsmD8AoHWeQgmxZ5yq8z0lXS67_QGs52AzC8Ru8'

    """
    if algorithm not in jwk.HASHES:
        raise JWTError("Algorithm %s not supported." % algorithm)

    for time_claim in ("exp", "iat", "nbf"):
        # Convert datetime to a intDate value in known time-format claims
        if isinstance(claims.get(time_claim), datetime):
            claims[time_claim] = timegm(claims[time_claim].utctimetuple())
    if access_token:
        claims["at_hash"] = _calculate_at_hash(access_token, jwk.HASHES[algorithm])

    encoded_headers = _encode_header(algorithm, headers)
    encoded_payload = _encode_payload(claims)
    return _sign_header_and_payload(encoded_headers, encoded_payload, algorithm, key)


def decode(token: str, key: str, algorithm, leeway=0, audience=None, issuer=None, subject=None, access_token=None):
    header, payload, signing_input, signature = load(token)
    verify(signing_input, signature, key, algorithm)
    claims = orjson.loads(payload)
    algorithm = header["alg"]

    _validate_claims(
        claims,
        leeway,
        audience=audience,
        issuer=issuer,
        subject=subject,
        algorithm=algorithm,
        access_token=access_token,
    )
    return claims


def _calculate_at_hash(access_token, hash_alg) -> str:
    """
    Args:
        access_token (str): An access token string.
        hash_alg (callable): A callable returning a hash object, e.g. hashlib.sha256
    """
    hash_digest = hash_alg(access_token.encode("utf-8")).digest()
    cut_at = int(len(hash_digest) / 2)
    truncated = hash_digest[:cut_at]
    at_hash = b64decode(truncated).replace(b"=", b"")
    return at_hash.decode("utf-8")


def _encode_header(algorithm, additional_headers=None) -> bytes:
    header = {"typ": "JWT", "alg": algorithm}
    if additional_headers:
        header.update(additional_headers)
    json_header = orjson.dumps(header)
    return b64encode(json_header)


def _encode_payload(payload) -> bytes:
    if isinstance(payload, Mapping):
        try:
            payload = orjson.dumps(payload)
        except ValueError:
            pass
    return b64encode(payload)


def _sign_header_and_payload(encoded_header, encoded_payload, algorithm, key) -> str:
    signing_input = encoded_header + b'.' + encoded_payload
    signature = sign(signing_input, key, algorithm)
    encoded_signature = b64encode(signature)
    return (b".".join([encoded_header, encoded_payload, encoded_signature])).decode('utf-8')


def _validate_claims(
    claims, leeway=0, audience=None, issuer=None, subject=None, algorithm=None, access_token=None
):
    if not isinstance(audience, ((str,), type(None))):
        raise JWTError("audience must be a string or None")

    _validate_iat(claims)
    _validate_nbf(claims, leeway=leeway)
    _validate_exp(claims, leeway=leeway)

    if audience:
        _validate_aud(claims, audience=audience)

    if issuer:
        _validate_iss(claims, issuer=issuer)

    if subject:
        _validate_sub(claims, subject=subject)

    _validate_jti(claims)

    if access_token:
        _validate_at_hash(claims, access_token, algorithm)


def _validate_iat(claims):
    """
    Validates that the 'iat' claim is valid.
    Args:
        claims (dict): The claims dictionary to validate.
    """

    if "iat" not in claims:
        return

    try:
        int(claims["iat"])
    except ValueError:
        raise JWTClaimsError("Issued At claim (iat) must be an integer.")


def _validate_nbf(claims, leeway=0):
    """
    Validates that the 'nbf' claim is valid.
    Args:
        claims (dict): The claims dictionary to validate.
        leeway (int): The number of seconds of skew that is allowed.
    """

    if "nbf" not in claims:
        return

    try:
        nbf = int(claims["nbf"])
    except ValueError:
        raise JWTClaimsError("Not Before claim (nbf) must be an integer.")

    now = timegm(datetime.utcnow().utctimetuple())

    if nbf > (now + leeway):
        raise JWTClaimsError("The token is not yet valid (nbf)")


def _validate_exp(claims, leeway=0):
    """
    Validates that the 'exp' claim is valid.
    Args:
        claims (dict): The claims dictionary to validate.
        leeway (int): The number of seconds of skew that is allowed.
    """

    if "exp" not in claims:
        return

    try:
        exp = int(claims["exp"])
    except ValueError:
        raise JWTClaimsError("Expiration Time claim (exp) must be an integer.")

    now = timegm(datetime.utcnow().utctimetuple())

    if exp < (now - leeway):
        raise ExpiredSignatureError("Signature has expired.")


def _validate_aud(claims, audience=None):
    """
    Validates that the 'aud' claim is valid.
    Args:
        claims (dict): The claims dictionary to validate.
        audience (str): The audience that is verifying the token.
    """

    if "aud" not in claims:
        if audience:
            raise JWTError('Audience claim expected, but not in claims')
        return

    audience_claims = claims["aud"]
    if isinstance(audience_claims, str):
        audience_claims = [audience_claims]
    if not isinstance(audience_claims, list):
        raise JWTClaimsError("Invalid claim format in token")
    if any(not isinstance(c, str) for c in audience_claims):
        raise JWTClaimsError("Invalid claim format in token")
    if audience not in audience_claims:
        raise JWTClaimsError("Invalid audience")


def _validate_iss(claims, issuer=None):
    """
    Validates that the 'iss' claim is valid.
    Args:
        claims (dict): The claims dictionary to validate.
        issuer (str or iterable): Acceptable value(s) for the issuer that
                                  signed the token.
    """

    if issuer is not None:
        if isinstance(issuer, str):
            issuer = (issuer,)
        if claims.get("iss") not in issuer:
            raise JWTClaimsError("Invalid issuer")


def _validate_sub(claims, subject=None):
    """
    Validates that the 'sub' claim is valid.
    Args:
        claims (dict): The claims dictionary to validate.
        subject (str): The subject of the token.
    """

    if "sub" not in claims:
        return

    if not isinstance(claims["sub"], str):
        raise JWTClaimsError("Subject must be a string.")

    if subject is not None and claims.get("sub") != subject:
        raise JWTClaimsError("Invalid subject")


def _validate_jti(claims):
    """
    Validates that the 'jti' claim is valid.
    Args:
        claims (dict): The claims dictionary to validate.
    """
    if "jti" not in claims:
        return

    if not isinstance(claims["jti"], str):
        raise JWTClaimsError("JWT ID must be a string.")


def _validate_at_hash(claims, access_token, algorithm):
    """
    Validates that the 'at_hash' is valid.
    Args:
      claims (dict): The claims dictionary to validate.
      access_token (str): The access token returned by the OpenID Provider.
      algorithm (str): The algorithm used to sign the JWT, as specified by
          the token headers.
    """
    if "at_hash" not in claims:
        return

    if not access_token:
        msg = "No access_token provided to compare against at_hash claim."
        raise JWTClaimsError(msg)

    try:
        expected_hash = _calculate_at_hash(access_token, jwk.HASHES[algorithm])
    except (TypeError, ValueError):
        msg = "Unable to calculate at_hash to verify against token claims."
        raise JWTClaimsError(msg)

    if claims["at_hash"] != expected_hash:
        raise JWTClaimsError("at_hash claim does not match access_token.")
