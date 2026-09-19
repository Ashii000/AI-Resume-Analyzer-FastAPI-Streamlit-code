"""SQLAlchemy ORM models for the application.

Models are defined using the SQLAlchemy Declarative API and include basic
indexes and relationships suitable for a production service.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """Representation of an application user.

    Attributes:
        id: Primary key.
        email: Unique email address used for login.
        hashed_password: bcrypt-hashed password.
        created_at: Timestamp when the user was created.
        resumes: Relationship to user's uploaded resumes.
    """

    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Token rotation / revocation support: store last valid refresh token jti
    refresh_token_jti: Optional[str] = Column(String(255), nullable=True)

    # Relationship: one user -> many resumes
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<User id={self.id} email={self.email}>"


class Resume(Base):
    """Uploaded resume metadata and parsed content.

    Attributes:
        id: Primary key.
        user_id: FK to user who uploaded the resume (optional for anonymous uploads).
        filename: Original filename.
        parsed_json: JSON blob with parsed fields (skills, education, etc.).
        created_at: Upload timestamp.
    """

    __tablename__ = "resumes"
    id: int = Column(Integer, primary_key=True, index=True)
    user_id: Optional[int] = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    filename: Optional[str] = Column(String(512), nullable=False)
    parsed_json: Optional[dict] = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="resumes")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<Resume id={self.id} filename={self.filename}>"


class Job(Base):
    """Basic job description record.

    Stores the original job text and extracted metadata for matching and history.
    """

    __tablename__ = "jobs"
    id: int = Column(Integer, primary_key=True, index=True)
    title: Optional[str] = Column(String(255), nullable=True)
    original_text: Optional[str] = Column(Text, nullable=True)
    parsed_json: Optional[dict] = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<Job id={self.id} title={self.title}>"


