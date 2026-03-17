import uuid
from datetime import datetime, date
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Numeric,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Discount(Base):
    """Coupon / discount definition at the organization or venue level."""

    __tablename__ = "discounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    venue_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=True
    )
    code: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # promo code; NULL = no code needed
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Type: flat_off | percent_off | free_slot
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    value_cents: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # for flat_off
    percent_off: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 0–100 for percent_off
    min_order_cents: Mapped[int] = mapped_column(
        Integer, default=0
    )  # minimum order amount

    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    max_uses: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # NULL = unlimited
    max_uses_per_user: Mapped[int | None] = mapped_column(Integer, nullable=True)
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
