"""Password hashing and validation utilities.

Uses passlib bcrypt for secure password hashing and provides simple
password strength validation rules suitable for production use.
"""
from __future__ import annotations

import re
import logging
from typing import Tuple
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Use pbkdf2_sha256 to avoid platform-specific bcrypt backend issues
# pbkdf2_sha256 is a secure, widely-supported algorithm and works without C extensions.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password.

    Returns:
        The bcrypt hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the stored bcrypt hash.

    Args:
        plain_password: The plaintext password to verify.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if the password matches; False otherwise.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:  # pragma: no cover - passlib internal failures
        logger.exception("Password verification failed")
        return False


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password strength against basic rules.

    Rules enforced:
    - Minimum length 8
    - Contains uppercase, lowercase, digit
    - Contains special character

    Args:
        password: Password to validate.

    Returns:
        Tuple of (is_valid, message). If valid, message is empty.
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    if not re.search(r"[\W_]", password):
        return False, "Password must contain at least one special character"

    return True, ""
