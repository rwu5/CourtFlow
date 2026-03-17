import uuid
from datetime import datetime, date, time
from sqlalchemy import String, Boolean, DateTime, Date, Time, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class OperatingSchedule(Base):
    """Day-of-week and date-specific operating hours for a venue.

    A date-specific record (specific_date is set) overrides the weekday default.
    """

    __tablename__ = "operating_schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False
    )
    # 0=Monday … 6=Sunday; NULL means date-specific override
    weekday: Mapped[int | None] = mapped_column(Integer, nullable=True)
    specific_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)

    venue: Mapped["Venue"] = relationship(back_populates="schedules")  # noqa: F821
