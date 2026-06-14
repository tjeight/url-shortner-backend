from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from src.configs.root_model import Base


# Class to handle the User URLS
class LinkUrl(Base):
    __tablename__ = "link_urls"

    link_url_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    long_url: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index(
            "idx_user_long_url",
            user_id,
            long_url,
        ),
        Index(
            "idx_user_active_created",
            user_id,
            is_active,
            created_at.desc(),
        ),
        Index(
            "idx_link_expires_at",
            expires_at,
        ),
    )
