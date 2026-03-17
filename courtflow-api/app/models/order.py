import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class OrderStatus(str, enum.Enum):
    pending = "pending"  # created, awaiting payment
    paid = "paid"  # fully paid
    partially_refunded = "partially_refunded"
    refunded = "refunded"
    cancelled = "cancelled"


class Order(Base):
    """Parent commerce entity.

    An order aggregates one or more reservations (or future: courses, merchandise).
    Payment is attached to the order, not individual reservations.
    """

    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(String(30), default=OrderStatus.pending)
    subtotal_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    discount_cents: Mapped[int] = mapped_column(Integer, default=0)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="order"
    )  # noqa: F821
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order"
    )  # noqa: F821


class OrderItem(Base):
    """Individual line item within an order."""

    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False
    )
    item_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # reservation | course | product
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    description: Mapped[str] = mapped_column(
        String(200), nullable=False
    )  # human-readable summary
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
