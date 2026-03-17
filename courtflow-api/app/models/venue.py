import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    address: Mapped[str] = mapped_column(String(256), nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    district: Mapped[str | None] = mapped_column(String(64), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    wechat_cs: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )  # WeChat CS QR or ID
    parking_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    open_time: Mapped[str] = mapped_column(String(5), default="07:00")  # "07:00"
    close_time: Mapped[str] = mapped_column(String(5), default="22:00")  # "22:00"
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)  # 30 or 60
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="venues"
    )  # noqa: F821
    media: Mapped[list["VenueMedia"]] = relationship(
        back_populates="venue", order_by="VenueMedia.sort_order"
    )
    facilities: Mapped[list["VenueFacility"]] = relationship(back_populates="venue")
    courts: Mapped[list["Court"]] = relationship(back_populates="venue")  # noqa: F821
    court_types: Mapped[list["CourtType"]] = relationship(
        back_populates="venue"
    )  # noqa: F821
    schedules: Mapped[list["OperatingSchedule"]] = relationship(
        back_populates="venue"
    )  # noqa: F821


class VenueMedia(Base):
    __tablename__ = "venue_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[str] = mapped_column(
        String(20), default="photo"
    )  # photo, banner, thumbnail
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    venue: Mapped["Venue"] = relationship(back_populates="media")


class VenueFacility(Base):
    __tablename__ = "venue_facilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False
    )
    key: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # e.g. "high_ceiling_court"
    label: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "高楼层球场"
    icon: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )  # icon name or URL
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)

    venue: Mapped["Venue"] = relationship(back_populates="facilities")
