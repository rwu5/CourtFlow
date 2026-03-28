from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.venue import Venue
from app.models.court import Court
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User

router = APIRouter(prefix="/reservations", tags=["admin-reservations"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class ReservationOut(BaseModel):
    id: str
    user_id: str
    court_id: str
    order_id: str | None
    slot_start_at: str
    slot_end_at: str
    status: str
    amount_cents: int
    contact_phone: str | None
    note: str | None
    checked_in_at: str | None
    cancelled_at: str | None
    cancel_reason: str | None
    created_at: str
    updated_at: str
    # Joined display fields
    user_nickname: str | None
    user_phone: str | None
    court_name: str
    venue_name: str
    venue_id: str


class PaginatedReservations(BaseModel):
    items: list[ReservationOut]
    total: int
    page: int
    page_size: int


class CancelBody(BaseModel):
    reason: str | None = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _get_org_venue_ids(db, org_id) -> list:
    result = await db.execute(
        select(Venue.id).where(Venue.organization_id == org_id)
    )
    return [row[0] for row in result.all()]


def _reservation_out(r: Reservation, court_name: str, venue_name: str,
                     venue_id, user_nickname: str | None,
                     user_phone: str | None) -> ReservationOut:
    return ReservationOut(
        id=str(r.id),
        user_id=str(r.user_id),
        court_id=str(r.court_id),
        order_id=str(r.order_id) if r.order_id else None,
        slot_start_at=r.slot_start_at.isoformat(),
        slot_end_at=r.slot_end_at.isoformat(),
        status=r.status if isinstance(r.status, str) else r.status.value,
        amount_cents=r.amount_cents,
        contact_phone=r.contact_phone,
        note=r.note,
        checked_in_at=r.checked_in_at.isoformat() if r.checked_in_at else None,
        cancelled_at=r.cancelled_at.isoformat() if r.cancelled_at else None,
        cancel_reason=r.cancel_reason,
        created_at=r.created_at.isoformat(),
        updated_at=r.updated_at.isoformat(),
        user_nickname=user_nickname,
        user_phone=user_phone,
        court_name=court_name,
        venue_name=venue_name,
        venue_id=str(venue_id),
    )


async def _get_reservation(db, reservation_id: str, venue_ids: list):
    """Fetch a single reservation with joined court/venue/user, scoped to org."""
    result = await db.execute(
        select(Reservation, Court.name, Venue.name, Venue.id, User.nickname, User.phone)
        .join(Court, Reservation.court_id == Court.id)
        .join(Venue, Court.venue_id == Venue.id)
        .outerjoin(User, Reservation.user_id == User.id)
        .where(Reservation.id == reservation_id, Venue.id.in_(venue_ids))
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return row


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedReservations)
async def list_reservations(
    venue_id: str | None = Query(None),
    court_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)

    base = (
        select(Reservation, Court.name, Venue.name, Venue.id, User.nickname, User.phone)
        .join(Court, Reservation.court_id == Court.id)
        .join(Venue, Court.venue_id == Venue.id)
        .outerjoin(User, Reservation.user_id == User.id)
        .where(Venue.id.in_(venue_ids))
    )

    if venue_id:
        base = base.where(Venue.id == venue_id)
    if court_id:
        base = base.where(Reservation.court_id == court_id)
    if date_from:
        base = base.where(Reservation.slot_start_at >= date_from)
    if date_to:
        base = base.where(Reservation.slot_start_at <= date_to + "T23:59:59+00:00")
    if status:
        base = base.where(Reservation.status == status)

    # Count
    count_q = select(func.count()).select_from(
        base.with_only_columns(Reservation.id).subquery()
    )
    total = (await db.execute(count_q)).scalar() or 0

    # Paginated results
    q = base.order_by(Reservation.slot_start_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)

    items = [
        _reservation_out(r, court_name, venue_name, vid, user_nick, user_phone)
        for r, court_name, venue_name, vid, user_nick, user_phone in result.all()
    ]

    return PaginatedReservations(items=items, total=total, page=page, page_size=page_size)


@router.get("/{reservation_id}", response_model=ReservationOut)
async def get_reservation(
    reservation_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    row = await _get_reservation(db, reservation_id, venue_ids)
    r, court_name, venue_name, vid, user_nick, user_phone = row
    return _reservation_out(r, court_name, venue_name, vid, user_nick, user_phone)


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
async def cancel_reservation(
    reservation_id: str,
    body: CancelBody,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    row = await _get_reservation(db, reservation_id, venue_ids)
    r, court_name, venue_name, vid, user_nick, user_phone = row

    cancelable = {
        ReservationStatus.held, ReservationStatus.pending_payment,
        ReservationStatus.confirmed, ReservationStatus.checked_in,
    }
    current = r.status if isinstance(r.status, ReservationStatus) else ReservationStatus(r.status)
    if current not in cancelable:
        raise HTTPException(status_code=400, detail=f"Cannot cancel reservation in '{r.status}' status")

    r.status = ReservationStatus.admin_cancelled
    r.cancelled_at = datetime.utcnow()
    r.cancel_reason = body.reason
    r.cancelled_by = user.id
    await db.commit()
    await db.refresh(r)
    return _reservation_out(r, court_name, venue_name, vid, user_nick, user_phone)


@router.post("/{reservation_id}/check-in", response_model=ReservationOut)
async def check_in_reservation(
    reservation_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    row = await _get_reservation(db, reservation_id, venue_ids)
    r, court_name, venue_name, vid, user_nick, user_phone = row

    current = r.status if isinstance(r.status, ReservationStatus) else ReservationStatus(r.status)
    if current != ReservationStatus.confirmed:
        raise HTTPException(status_code=400, detail=f"Can only check in confirmed reservations, current: '{r.status}'")

    r.status = ReservationStatus.checked_in
    r.checked_in_at = datetime.utcnow()
    await db.commit()
    await db.refresh(r)
    return _reservation_out(r, court_name, venue_name, vid, user_nick, user_phone)


@router.post("/{reservation_id}/no-show", response_model=ReservationOut)
async def no_show_reservation(
    reservation_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    row = await _get_reservation(db, reservation_id, venue_ids)
    r, court_name, venue_name, vid, user_nick, user_phone = row

    allowed = {ReservationStatus.confirmed, ReservationStatus.checked_in}
    current = r.status if isinstance(r.status, ReservationStatus) else ReservationStatus(r.status)
    if current not in allowed:
        raise HTTPException(status_code=400, detail=f"Cannot mark no-show from '{r.status}' status")

    r.status = ReservationStatus.no_show
    await db.commit()
    await db.refresh(r)
    return _reservation_out(r, court_name, venue_name, vid, user_nick, user_phone)


@router.post("/{reservation_id}/complete", response_model=ReservationOut)
async def complete_reservation(
    reservation_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    row = await _get_reservation(db, reservation_id, venue_ids)
    r, court_name, venue_name, vid, user_nick, user_phone = row

    current = r.status if isinstance(r.status, ReservationStatus) else ReservationStatus(r.status)
    if current != ReservationStatus.checked_in:
        raise HTTPException(status_code=400, detail=f"Can only complete checked-in reservations, current: '{r.status}'")

    r.status = ReservationStatus.completed
    await db.commit()
    await db.refresh(r)
    return _reservation_out(r, court_name, venue_name, vid, user_nick, user_phone)
