import uuid
from datetime import datetime, date, time
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Date,
    Time,
    ForeignKey,
    Numeric,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class PricingRule(Base):
    """Dynamic pricing rule evaluated by priority.

    Rules are evaluated highest-priority-first. First match wins.
    amount_cents is the price in fen (Chinese cents).
    original_amount_cents is the strikethrough/original price shown in UI.
    """

    __tablename__ = "pricing_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False
    )
    court_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id"), nullable=True
    )
    court_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("court_types.id"), nullable=True
    )
    membership_tier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("membership_tiers.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    priority: Mapped[int] = mapped_column(
        Integer, default=0
    )  # higher = evaluated first

    # Time conditions (all optional — NULL = any)
    weekdays: Mapped[str | None] = mapped_column(
        String(13), nullable=True
    )  # "0,1,2,3,4" (Mon-Fri)
    date_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    time_from: Mapped[time | None] = mapped_column(Time, nullable=True)  # slot start >=
    time_to: Mapped[time | None] = mapped_column(Time, nullable=True)  # slot start <
    is_holiday: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )  # NULL = don't check

    # Price
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)  # actual price
    original_amount_cents: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # strikethrough

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
