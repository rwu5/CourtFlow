"""Booking hold and release endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.booking import (
    hold_slots,
    release_hold,
    HoldRequest,
    SlotUnavailableError,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


class HoldSlotItem(BaseModel):
    court_id: str
    slot_start: datetime  # UTC ISO8601
    slot_end: datetime


class HoldSlotsRequest(BaseModel):
    venue_id: str
    slots: list[HoldSlotItem]
    contact_phone: str | None = None


class HoldSlotOut(BaseModel):
    reservation_id: str
    court_id: str
    slot_start: str
    slot_end: str
    amount_cents: int
    hold_expires_at: str


class HoldSlotsResponse(BaseModel):
    holds: list[HoldSlotOut]


@router.post("/hold", response_model=HoldSlotsResponse)
async def hold(
    body: HoldSlotsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.main import app

    redis = app.state.redis

    hold_requests = [
        HoldRequest(court_id=s.court_id, slot_start=s.slot_start, slot_end=s.slot_end)
        for s in body.slots
    ]

    try:
        reservations = await hold_slots(
            db, redis, current_user.id, hold_requests, body.contact_phone
        )
    except SlotUnavailableError as e:
        raise HTTPException(status_code=409, detail=str(e))

    await db.commit()

    return HoldSlotsResponse(
        holds=[
            HoldSlotOut(
                reservation_id=str(r.id),
                court_id=str(r.court_id),
                slot_start=r.slot_start_at.isoformat(),
                slot_end=r.slot_end_at.isoformat(),
                amount_cents=r.amount_cents,
                hold_expires_at=r.hold_expires_at.isoformat(),
            )
            for r in reservations
        ]
    )


@router.delete("/hold/{reservation_id}", status_code=204)
async def release(
    reservation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.main import app

    redis = app.state.redis
    import uuid

    await release_hold(db, redis, uuid.UUID(reservation_id), current_user.id)
    await db.commit()
