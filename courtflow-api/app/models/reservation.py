import uuid
from datetime import datetime
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class ReservationStatus(str, enum.Enum):
    held = "held"  # slot locked for user, awaiting payment
    pending_payment = "pending_payment"  # order submitted, payment initiated
    payment_failed = "payment_failed"  # payment attempt failed
    confirmed = "confirmed"  # payment successful
    checked_in = "checked_in"  # user arrived at venue
    completed = "completed"  # session ended
    cancelled = "cancelled"  # user cancelled
    admin_cancelled = "admin_cancelled"  # operator cancelled
    no_show = "no_show"  # user did not appear
    refunded = "refunded"  # full refund issued
    partially_refunded = "partially_refunded"  # partial refund


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        # Prevent double-booking: one confirmed/held reservation per court+slot
        UniqueConstraint(
            "court_id",
            "slot_start_at",
            name="uq_court_slot",
            # This constraint is partial — only active reservations count.
            # Enforced at application layer for cancelled/refunded states.
        ),
        Index("ix_reservations_court_slot", "court_id", "slot_start_at"),
        Index("ix_reservations_user", "user_id"),
        Index("ix_reservations_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True
    )
    slot_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    slot_end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[ReservationStatus] = mapped_column(
        String(30), default=ReservationStatus.held, nullable=False
    )
    hold_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    amount_cents: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # price at time of booking
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Admin fields
    checked_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancel_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cancelled_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship()  # noqa: F821
    court: Mapped["Court"] = relationship()  # noqa: F821
    order: Mapped["Order | None"] = relationship(
        back_populates="reservations"
    )  # noqa: F821
