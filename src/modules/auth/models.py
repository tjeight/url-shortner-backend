from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from src.configs.root_model import Base


# Class to handle the authentication module
class Users(Base):
    __tablename__ = "users"
    user_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    user_email: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=func.now(), nullable=False
    )

    __table_args__ = (Index("unique_email_index", user_email),)


# Class to Handle the User Session
class UserSession(Base):
    __tablename__ = "user_sessions"

    user_session_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    # store the hash of the refresh token
    refresh_token_hash: Mapped[str] = mapped_column(String, nullable=True)
    device_info: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, onupdate=func.now(), default=func.now()
    )
