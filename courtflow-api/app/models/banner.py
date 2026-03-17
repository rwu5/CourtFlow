import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Banner(Base):
    """Home page carousel and promotional banners, scoped to an organization."""

    __tablename__ = "banners"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    link_type: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # venue | url | none
    link_value: Mapped[str | None] = mapped_column(String(256), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
