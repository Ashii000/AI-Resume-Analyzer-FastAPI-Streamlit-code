"""JWT creation, verification and helpers.

Uses python-jose to sign and verify JWT tokens. Supports access tokens,
refresh tokens, and password reset tokens. Tokens include a jti (UUID) to
support rotation and revocation when combined with a persistent store.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid

from jose import jwt, JWTError

from app.config import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"


def _now() -> datetime:
    return datetime.utcnow()


def _jti() -> str:
    return str(uuid.uuid4())


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Subject identifier (typically user id).
        expires_delta: Optional timedelta for token expiry. Defaults to 15 minutes.

    Returns:
        Encoded JWT string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=15)
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "exp": int((_now() + expires_delta).timestamp()),
        "iat": int(_now().timestamp()),
    }
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> Dict[str, Any]:
    """Create a signed JWT refresh token and return its token and metadata.

    Returns a dict containing token string and the jti.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=7)
    jti = _jti()
    to_encode = {
        "sub": str(subject),
        "type": "refresh",
        "exp": int((_now() + expires_delta).timestamp()),
        "iat": int(_now().timestamp()),
        "jti": jti,
    }
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "jti": jti}


def create_password_reset_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a password reset token (short-lived).

    Args:
        subject: Typically user id or email.
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=1)
    to_encode = {"sub": str(subject), "type": "password_reset", "exp": int((_now() + expires_delta).timestamp()), "iat": int(_now().timestamp())}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token, returning its payload.

    Raises:
        jose.JWTError if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        logger.debug("Token decode failed: %s", exc)
        raise


def verify_token_type(token: str, expected_type: str) -> Dict[str, Any]:
    """Decode token and assert it is of the expected type.

    Raises:
        JWTError if invalid or wrong type.
    """
    payload = decode_token(token)
    t = payload.get("type")
    if t != expected_type:
        raise JWTError(f"Invalid token type: expected {expected_type} got {t}")
    return payload
