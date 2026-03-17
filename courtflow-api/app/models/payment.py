import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    refunded = "refunded"
    partially_refunded = "partially_refunded"


class PaymentProvider(str, enum.Enum):
    wechat_pay = "wechat_pay"
    alipay = "alipay"
    manual = "manual"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False
    )
    provider: Mapped[PaymentProvider] = mapped_column(String(20), nullable=False)
    provider_order_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )  # WeChat/Alipay trade no
    provider_transaction_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    refunded_cents: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[PaymentStatus] = mapped_column(
        String(30), default=PaymentStatus.pending
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # provider response
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    order: Mapped["Order"] = relationship(back_populates="payments")  # noqa: F821


class PaymentAccount(Base):
    """Payment provider account credentials per organization."""

    __tablename__ = "payment_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    provider: Mapped[PaymentProvider] = mapped_column(String(20), nullable=False)
    config_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # encrypted provider creds
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
