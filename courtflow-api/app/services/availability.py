"""Availability engine — computes the booking grid for a venue on a date range.

Returns a structured grid keyed by (court_id, slot_start_iso) → SlotInfo.

Redis cache key: availability:{venue_id}:{date}
TTL: 30 seconds
"""

from __future__ import annotations

import json
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo
from dataclasses import dataclass, asdict
from typing import Literal

from redis.asyncio import Redis
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.court import Court, CourtBlock
from app.models.reservation import Reservation, ReservationStatus
from app.models.venue import Venue
from app.services.pricing import resolve_price

CACHE_TTL = 30  # seconds


@dataclass
class SlotInfo:
    court_id: str
    slot_start: str  # ISO8601 UTC
    slot_end: str
    status: Literal["available", "unavailable", "booked", "locked"]
    amount_cents: int | None
    original_amount_cents: int | None


async def get_availability_grid(
    db: AsyncSession,
    redis: Redis,
    venue_id: str,
    target_date: date,
    user_id: str | None = None,
) -> dict[str, dict[str, SlotInfo]]:
    """Return {court_id: {slot_start_iso: SlotInfo}} for target_date.

    Tries Redis cache first; falls back to DB computation.
    """
    cache_key = f"availability:{venue_id}:{target_date.isoformat()}"
    cached = await redis.get(cache_key)
    if cached:
        raw: dict = json.loads(cached)
        return {
            court_id: {k: SlotInfo(**v) for k, v in slots.items()}
            for court_id, slots in raw.items()
        }

    grid = await _compute_grid(db, venue_id, target_date)
    await redis.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(
            {
                cid: {k: asdict(v) for k, v in slots.items()}
                for cid, slots in grid.items()
            }
        ),
    )
    return grid


async def invalidate_availability(
    redis: Redis, venue_id: str, target_date: date
) -> None:
    cache_key = f"availability:{venue_id}:{target_date.isoformat()}"
    await redis.delete(cache_key)


async def _compute_grid(
    db: AsyncSession,
    venue_id: str,
    target_date: date,
) -> dict[str, dict[str, SlotInfo]]:
    venue_result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = venue_result.scalar_one()
    tz = ZoneInfo(venue.timezone)

    # Build list of slot start times (local) for the day
    open_h, open_m = map(int, venue.open_time.split(":"))
    close_h, close_m = map(int, venue.close_time.split(":"))
    slot_duration = timedelta(minutes=venue.slot_duration_minutes)

    current = datetime(
        target_date.year, target_date.month, target_date.day, open_h, open_m, tzinfo=tz
    )
    close = datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        close_h,
        close_m,
        tzinfo=tz,
    )
    slot_starts: list[datetime] = []
    while current < close:
        slot_starts.append(current)
        current += slot_duration

    # Load courts
    courts_result = await db.execute(
        select(Court)
        .where(Court.venue_id == venue_id, Court.is_active == True)  # noqa: E712
        .order_by(Court.sort_order)
    )
    courts = courts_result.scalars().all()

    # Load active reservations for this day
    day_start = datetime(
        target_date.year, target_date.month, target_date.day, tzinfo=tz
    ).astimezone(timezone.utc)
    day_end = day_start + timedelta(days=1)
    court_ids = [c.id for c in courts]

    reservations_result = await db.execute(
        select(Reservation).where(
            Reservation.court_id.in_(court_ids),
            Reservation.slot_start_at >= day_start,
            Reservation.slot_start_at < day_end,
            Reservation.status.in_(
                [
                    ReservationStatus.held,
                    ReservationStatus.pending_payment,
                    ReservationStatus.confirmed,
                    ReservationStatus.checked_in,
                ]
            ),
        )
    )
    reservations = reservations_result.scalars().all()
    booked_slots: set[tuple] = {
        (str(r.court_id), r.slot_start_at.astimezone(timezone.utc).isoformat())
        for r in reservations
    }

    # Load court blocks for the day
    blocks_result = await db.execute(
        select(CourtBlock).where(
            CourtBlock.court_id.in_(court_ids),
            CourtBlock.start_at < day_end,
            CourtBlock.end_at > day_start,
        )
    )
    blocks = blocks_result.scalars().all()

    now_utc = datetime.now(timezone.utc)
    grid: dict[str, dict[str, SlotInfo]] = {}

    for court in courts:
        grid[str(court.id)] = {}
        for slot_start_local in slot_starts:
            slot_start_utc = slot_start_local.astimezone(timezone.utc)
            slot_end_utc = slot_start_utc + slot_duration
            slot_key = slot_start_utc.isoformat()

            # Determine status
            if slot_start_utc < now_utc:
                status = "unavailable"
                amount_cents = None
                original_amount_cents = None
            elif _is_blocked(court.id, slot_start_utc, slot_end_utc, blocks):
                status = "unavailable"
                amount_cents = None
                original_amount_cents = None
            elif (str(court.id), slot_key) in booked_slots:
                status = "booked"
                amount_cents = None
                original_amount_cents = None
            else:
                status = "available"
                try:
                    amount_cents, original_amount_cents = await resolve_price(
                        db, court, slot_start_utc
                    )
                except ValueError:
                    status = "unavailable"
                    amount_cents = None
                    original_amount_cents = None

            grid[str(court.id)][slot_key] = SlotInfo(
                court_id=str(court.id),
                slot_start=slot_key,
                slot_end=slot_end_utc.isoformat(),
                status=status,
                amount_cents=amount_cents,
                original_amount_cents=original_amount_cents,
            )

    return grid


def _is_blocked(
    court_id, slot_start: datetime, slot_end: datetime, blocks: list[CourtBlock]
) -> bool:
    for block in blocks:
        if str(block.court_id) != str(court_id):
            continue
        if block.start_at < slot_end and block.end_at > slot_start:
            return True
    return False
