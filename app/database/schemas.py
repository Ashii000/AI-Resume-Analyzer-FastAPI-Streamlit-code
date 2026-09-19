"""Pydantic (v2) schemas for request/response models.

These schemas use `model_config = ConfigDict(from_attributes=True)` so they can
be constructed directly from SQLAlchemy ORM model instances.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class UserCreate(BaseModel):
    """Schema for creating a new user.

    Note: raw passwords should be hashed by the application service before
    being stored in the database.
    """

    email: str
    password: str


class UserRead(BaseModel):
    """Public representation of a user."""

    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeCreate(BaseModel):
    """Schema for uploading/creating a resume record."""

    user_id: Optional[int]
    filename: str
    parsed_json: Optional[Dict[str, Any]] = None


class ResumeRead(BaseModel):
    """Resume payload returned by the API."""

    id: int
    filename: str
    parsed_json: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobCreate(BaseModel):
    """Schema for creating a job description record."""

    title: Optional[str]
    original_text: Optional[str]
    parsed_json: Optional[Dict[str, Any]] = None


class JobRead(BaseModel):
    """Job payload returned by the API."""

    id: int
    title: Optional[str]
    parsed_json: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
