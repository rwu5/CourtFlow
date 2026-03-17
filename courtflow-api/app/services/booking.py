"""Booking service — hold, release, confirm, cancel.

Hold strategy:
  1. Check Redis lock (atomic SETNX) — fast rejection of concurrent holds
  2. Check DB for existing active reservation — authoritative
  3. Write DB reservation (status=held)
  4. Set Redis hold key with TTL
  5. Schedule async job to expire hold

This gives three layers of double-booking prevention.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from redis.asyncio import Redis
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.court import Court, CourtLink
from app.models.reservation import Reservation, ReservationStatus
from app.models.venue import Venue
from app.services.availability import invalidate_availability
from app.services.pricing import resolve_price

HOLD_TTL_SECONDS = 300  # 5 minutes


class SlotUnavailableError(Exception):
    pass


class HoldRequest:
    def __init__(self, court_id: str, slot_start: datetime, slot_end: datetime):
        self.court_id = court_id
        self.slot_start = slot_start  # UTC
        self.slot_end = slot_end


async def hold_slots(
    db: AsyncSession,
    redis: Redis,
    user_id: uuid.UUID,
    holds: list[HoldRequest],
    contact_phone: str | None = None,
) -> list[Reservation]:
    """Attempt to hold multiple slots atomically.

    If any slot is unavailable, raises SlotUnavailableError and holds nothing.
    """
    created: list[Reservation] = []
    redis_keys_set: list[str] = []

    try:
        for hold in holds:
            reservation, redis_key = await _hold_single_slot(
                db, redis, user_id, hold, contact_phone
            )
            created.append(reservation)
            redis_keys_set.append(redis_key)

        await db.flush()
        return created

    except SlotUnavailableError:
        # Roll back any holds already set in Redis this request
        for key in redis_keys_set:
            await redis.delete(key)
        await db.rollback()
        raise


async def _hold_single_slot(
    db: AsyncSession,
    redis: Redis,
    user_id: uuid.UUID,
    hold: HoldRequest,
    contact_phone: str | None,
) -> tuple[Reservation, str]:
    court_id = (
        uuid.UUID(hold.court_id) if isinstance(hold.court_id, str) else hold.court_id
    )

    # Layer 1: Redis optimistic lock
    redis_key = f"slot_hold:{hold.court_id}:{hold.slot_start.isoformat()}"
    acquired = await redis.set(redis_key, str(user_id), nx=True, ex=HOLD_TTL_SECONDS)
    if not acquired:
        raise SlotUnavailableError(
            f"Slot {hold.court_id}@{hold.slot_start} is taken (redis)"
        )

    # Layer 2: DB check for active reservation
    conflict = await db.execute(
        select(Reservation).where(
            Reservation.court_id == court_id,
            Reservation.slot_start_at == hold.slot_start,
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
    if conflict.scalar_one_or_none():
        await redis.delete(redis_key)
        raise SlotUnavailableError(
            f"Slot {hold.court_id}@{hold.slot_start} is taken (db)"
        )

    # Resolve price
    court_result = await db.execute(select(Court).where(Court.id == court_id))
    court = court_result.scalar_one()
    amount_cents, _ = await resolve_price(db, court, hold.slot_start)

    # Layer 3: DB write
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=HOLD_TTL_SECONDS)
    reservation = Reservation(
        user_id=user_id,
        court_id=court_id,
        slot_start_at=hold.slot_start,
        slot_end_at=hold.slot_end,
        status=ReservationStatus.held,
        hold_expires_at=expires_at,
        amount_cents=amount_cents,
        contact_phone=contact_phone,
    )
    db.add(reservation)

    # Invalidate availability cache for this date
    venue_result = await db.execute(select(Venue).where(Venue.id == court.venue_id))
    venue = venue_result.scalar_one()
    local_date = hold.slot_start.astimezone(ZoneInfo(venue.timezone)).date()
    await invalidate_availability(redis, str(venue.id), local_date)

    return reservation, redis_key


async def release_hold(
    db: AsyncSession,
    redis: Redis,
    reservation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Release a held reservation (user abandons checkout)."""
    result = await db.execute(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.user_id == user_id,
            Reservation.status == ReservationStatus.held,
        )
    )
    reservation = result.scalar_one_or_none()
    if not reservation:
        return

    reservation.status = ReservationStatus.cancelled
    reservation.cancelled_at = datetime.now(timezone.utc)
    await db.flush()

    redis_key = (
        f"slot_hold:{reservation.court_id}:{reservation.slot_start_at.isoformat()}"
    )
    await redis.delete(redis_key)


async def confirm_reservations(
    db: AsyncSession,
    redis: Redis,
    order_id: uuid.UUID,
) -> None:
    """Mark all reservations in an order as confirmed after successful payment."""
    result = await db.execute(
        select(Reservation).where(Reservation.order_id == order_id)
    )
    reservations = result.scalars().all()
    for res in reservations:
        res.status = ReservationStatus.confirmed
    await db.flush()


async def cancel_reservation(
    db: AsyncSession,
    redis: Redis,
    reservation_id: uuid.UUID,
    cancelled_by: uuid.UUID,
    reason: str | None = None,
    is_admin: bool = False,
) -> Reservation:
    result = await db.execute(
        select(Reservation).where(Reservation.id == reservation_id)
    )
    reservation = result.scalar_one_or_none()
    if not reservation:
        raise ValueError("Reservation not found")

    if reservation.status not in (
        ReservationStatus.confirmed,
        ReservationStatus.held,
        ReservationStatus.pending_payment,
    ):
        raise ValueError(f"Cannot cancel reservation in status {reservation.status}")

    reservation.status = (
        ReservationStatus.admin_cancelled if is_admin else ReservationStatus.cancelled
    )
    reservation.cancelled_at = datetime.now(timezone.utc)
    reservation.cancel_reason = reason
    reservation.cancelled_by = cancelled_by
    await db.flush()

    # Free availability cache
    court_result = await db.execute(
        select(Court).where(Court.id == reservation.court_id)
    )
    court = court_result.scalar_one()
    venue_result = await db.execute(select(Venue).where(Venue.id == court.venue_id))
    venue = venue_result.scalar_one()
    local_date = reservation.slot_start_at.astimezone(ZoneInfo(venue.timezone)).date()
    await invalidate_availability(redis, str(venue.id), local_date)

    return reservation
