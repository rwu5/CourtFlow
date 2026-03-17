"""Background task: expire held reservations whose TTL has passed.

Run via ARQ worker or a scheduled cron every minute.
"""

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation, ReservationStatus


async def expire_stale_holds(db: AsyncSession) -> int:
    """Set status=cancelled for all held reservations past hold_expires_at.

    Returns the number of reservations expired.
    """
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Reservation).where(
            Reservation.status == ReservationStatus.held,
            Reservation.hold_expires_at < now,
        )
    )
    stale = result.scalars().all()

    for res in stale:
        res.status = ReservationStatus.cancelled
        res.cancelled_at = now
        res.cancel_reason = "hold_expired"

    if stale:
        await db.commit()

    return len(stale)
