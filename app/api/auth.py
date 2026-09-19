"""Authentication API: registration, login, refresh, password reset, logout.

This module implements a clean, dependency-injected set of endpoints using
SQLAlchemy sessions for persistence and JWT-based auth for tokens.
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import models
from app.database.schemas import UserRead, UserCreate
from app.auth.hashing import hash_password, verify_password, validate_password_strength
from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    verify_token_type,
    decode_token,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new user with email and password.

    Validates password strength and stores a bcrypt-hashed password.

    Args:
        user_in: UserCreate payload with email and password.
        db: SQLAlchemy session dependency.

    Returns:
        The created user as UserRead.
    """
    email = user_in.email
    password = user_in.password

    # Basic validation
    is_valid, msg = validate_password_strength(password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    # Check existing user
    existing = db.execute(select(models.User).where(models.User.email == email)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user = models.User(email=email, hashed_password=hash_password(password))
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as exc:  # pragma: no cover - DB failures
        logger.exception("Failed to create user: %s", exc)
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to create user")


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Authenticate user and return access + refresh tokens.

    Accepts OAuth2PasswordRequestForm for compatibility with standard flows.
    """
    user = db.execute(select(models.User).where(models.User.email == form_data.username)).scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(subject=str(user.id))
    refresh = create_refresh_token(subject=str(user.id))

    # Persist the refresh token jti for single active refresh token support
    try:
        user.refresh_token_jti = refresh["jti"]
        db.add(user)
        db.commit()
    except Exception:
        db.rollback()

    return {"access_token": access_token, "refresh_token": refresh["token"], "token_type": "bearer"}


@router.post("/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Exchange a refresh token for a new access token (and rotate refresh token).

    The refresh token must be valid and match the stored jti on the user record.
    """
    try:
        payload = verify_token_type(refresh_token, "refresh")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    jti = payload.get("jti")
    user = db.get(models.User, int(user_id))
    if not user or not user.refresh_token_jti or user.refresh_token_jti != jti:
        raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")

    # Issue rotated refresh token and new access token
    access_token = create_access_token(subject=str(user.id))
    new_refresh = create_refresh_token(subject=str(user.id))
    try:
        user.refresh_token_jti = new_refresh["jti"]
        db.add(user)
        db.commit()
    except Exception:
        db.rollback()

    return {"access_token": access_token, "refresh_token": new_refresh["token"], "token_type": "bearer"}


@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Log out a user by revoking their stored refresh token.

    This implementation clears the stored refresh_token_jti so the token cannot be used again.
    """
    try:
        payload = verify_token_type(refresh_token, "refresh")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.get(models.User, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.refresh_token_jti = None
    try:
        db.add(user)
        db.commit()
    except Exception:
        db.rollback()

    return {"msg": "logged_out"}


@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Generate a password reset token for the user.

    NOTE: In production, this token should be emailed to the user. For security,
    the token is short-lived and single-purpose.
    """
    user = db.execute(select(models.User).where(models.User.email == email)).scalars().first()
    if not user:
        # Don't reveal whether an account exists
        return {"msg": "If an account exists, a reset link has been sent"}

    token = create_password_reset_token(subject=str(user.id))
    # TODO: send email with token (outside scope). Return token for now.
    return {"reset_token": token}


@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Reset a user's password using a password reset token.

    Validates the token and sets the new hashed password.
    """
    try:
        payload = verify_token_type(token, "password_reset")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_id = payload.get("sub")
    user = db.get(models.User, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_valid, msg = validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    user.hashed_password = hash_password(new_password)
    try:
        db.add(user)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reset password")

    return {"msg": "password_reset"}
