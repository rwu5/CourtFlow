import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Time, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class CourtType(Base):
    """Named court categories per venue (e.g. 标准场, 学练场, 球道8米)"""

    __tablename__ = "court_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)  # 基础学练场
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    venue: Mapped["Venue"] = relationship(back_populates="court_types")  # noqa: F821
    courts: Mapped[list["Court"]] = relationship(back_populates="court_type")


class Court(Base):
    __tablename__ = "courts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False
    )
    court_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("court_types.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)  # 场地01
    surface: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # hard, clay, grass, synthetic
    is_indoor: Mapped[bool] = mapped_column(Boolean, default=True)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)  # 30 or 60
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    venue: Mapped["Venue"] = relationship(back_populates="courts")  # noqa: F821
    court_type: Mapped["CourtType | None"] = relationship(back_populates="courts")
    media: Mapped[list["CourtMedia"]] = relationship(
        back_populates="court", order_by="CourtMedia.sort_order"
    )
    blocks: Mapped[list["CourtBlock"]] = relationship(back_populates="court")
    # courts this court is linked to (for linked-court locking)
    links_from: Mapped[list["CourtLink"]] = relationship(
        foreign_keys="CourtLink.court_id", back_populates="court"
    )


class CourtMedia(Base):
    """Photos and media for a court"""

    __tablename__ = "court_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[str] = mapped_column(
        String(20), default="photo"
    )  # photo, banner, thumbnail
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    court: Mapped["Court"] = relationship(back_populates="media")


class CourtBlock(Base):
    """Maintenance windows and manual closures for a court"""

    __tablename__ = "court_blocks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    court: Mapped["Court"] = relationship(back_populates="blocks")


class CourtLink(Base):
    """Links two courts so booking one auto-locks the other (关联锁场)"""

    __tablename__ = "court_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False
    )
    linked_court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    court: Mapped["Court"] = relationship(
        foreign_keys=[court_id], back_populates="links_from"
    )
    linked_court: Mapped["Court"] = relationship(foreign_keys=[linked_court_id])
