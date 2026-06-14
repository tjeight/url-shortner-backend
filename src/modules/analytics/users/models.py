from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from src.configs.root_model import Base
from uuid import UUID
from uuid6 import uuid7


# Model to handle the URL Clicks
class URLClick(Base):
    __tablename__ = "url_clicks"
    url_click_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    link_url_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("link_urls.link_url_id", ondelete="CASCADE"), nullable=False
    )
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    user_agent: Mapped[str] = mapped_column(String, nullable=True)
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    # DB Attributes
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "idx_click_url_time",
            link_url_id,
            clicked_at.desc(),
        ),
    )
