import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class AuditLog(Base):
    """Immutable audit trail for all booking state changes and admin actions."""

    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    actor_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # user | admin | system
    action: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # e.g. reservation.confirmed
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    before_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
