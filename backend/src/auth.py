import os
import requests
from jose import jwt
from jose.utils import base64url_decode

COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")

COGNITO_ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

_jwks_cache = None


def get_jwks():
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache

    resp = requests.get(JWKS_URL, timeout=5)
    resp.raise_for_status()
    _jwks_cache = resp.json()
    return _jwks_cache


def verify_cognito_jwt(token: str, audience: str | None = None) -> dict:
    jwks = get_jwks()

    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")

    if not kid:
        raise Exception("Invalid token header (no kid)")

    key = None
    for k in jwks["keys"]:
        if k["kid"] == kid:
            key = k
            break

    if not key:
        raise Exception("Public key not found in JWKS")

    options = {
        "verify_signature": True,
        "verify_aud": bool(audience),
        "verify_exp": True,
        "verify_iss": True,
    }

    payload = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        audience=audience,
        issuer=COGNITO_ISSUER,
        options=options,
    )

    return payload