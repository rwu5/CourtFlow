from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.deps import get_current_user_optional
from app.models.user import User
from app.models.venue import Venue, VenueMedia, VenueFacility
from app.models.court import Court, CourtType
from app.services.availability import get_availability_grid, SlotInfo

router = APIRouter(prefix="/venues", tags=["venues"])


class VenueListItem(BaseModel):
    id: str
    name: str
    address: str
    city: str
    latitude: float | None
    longitude: float | None
    open_time: str
    close_time: str
    thumbnail_url: str | None
    is_partner: bool

    model_config = {"from_attributes": True}


class FacilityOut(BaseModel):
    key: str
    label: str
    icon: str | None
    description: str | None


class CourtTypeOut(BaseModel):
    id: str
    name: str
    description: str | None


class VenueDetailResponse(BaseModel):
    id: str
    name: str
    address: str
    city: str
    district: str | None
    latitude: float | None
    longitude: float | None
    phone: str | None
    wechat_cs: str | None
    parking_info: str | None
    open_time: str
    close_time: str
    slot_duration_minutes: int
    is_partner: bool
    photos: list[str]
    facilities: list[FacilityOut]
    court_types: list[CourtTypeOut]


class CourtMeta(BaseModel):
    id: str
    name: str
    is_indoor: bool
    surface: str | None
    court_type_id: str | None
    sort_order: int


class SlotOut(BaseModel):
    court_id: str
    slot_start: str
    slot_end: str
    status: str
    amount_cents: int | None
    original_amount_cents: int | None


class AvailabilityResponse(BaseModel):
    courts: list[CourtMeta]
    slots: dict[str, dict[str, SlotOut]]


@router.get("", response_model=list[VenueListItem])
async def list_venues(
    is_partner: bool | None = Query(None),
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    q = select(Venue).where(Venue.is_active == True)  # noqa: E712
    if is_partner is not None:
        q = q.where(Venue.organization.has(is_partner=is_partner))
    if city:
        q = q.where(Venue.city == city)

    result = await db.execute(q)
    venues = result.scalars().all()

    out = []
    for v in venues:
        thumb = next(
            (m.url for m in v.media if m.media_type == "thumbnail"),
            next((m.url for m in v.media if m.media_type in ("photo", "banner")), None),
        )
        out.append(
            VenueListItem(
                id=str(v.id),
                name=v.name,
                address=v.address,
                city=v.city,
                latitude=float(v.latitude) if v.latitude else None,
                longitude=float(v.longitude) if v.longitude else None,
                open_time=v.open_time,
                close_time=v.close_time,
                thumbnail_url=thumb,
                is_partner=v.organization.is_partner if v.organization else False,
            )
        )
    return out


@router.get("/{venue_id}", response_model=VenueDetailResponse)
async def get_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Venue).where(Venue.id == venue_id, Venue.is_active == True)
    )  # noqa: E712
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    photos = [
        m.url
        for m in sorted(venue.media, key=lambda m: m.sort_order)
        if m.media_type == "photo"
    ]

    return VenueDetailResponse(
        id=str(venue.id),
        name=venue.name,
        address=venue.address,
        city=venue.city,
        district=venue.district,
        latitude=float(venue.latitude) if venue.latitude else None,
        longitude=float(venue.longitude) if venue.longitude else None,
        phone=venue.phone,
        wechat_cs=venue.wechat_cs,
        parking_info=venue.parking_info,
        open_time=venue.open_time,
        close_time=venue.close_time,
        slot_duration_minutes=venue.slot_duration_minutes,
        is_partner=venue.organization.is_partner if venue.organization else False,
        photos=photos,
        facilities=[
            FacilityOut(
                key=f.key, label=f.label, icon=f.icon, description=f.description
            )
            for f in venue.facilities
        ],
        court_types=[
            CourtTypeOut(id=str(ct.id), name=ct.name, description=ct.description)
            for ct in sorted(venue.court_types, key=lambda ct: ct.sort_order)
        ],
    )


@router.get("/{venue_id}/availability", response_model=AvailabilityResponse)
async def get_availability(
    venue_id: str,
    target_date: Annotated[date, Query(alias="date")],
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Return booking grid for venue on a given date.

    Response includes:
      - courts: list of CourtMeta (with is_indoor, surface, etc.)
      - slots: {court_id: {slot_start_iso: SlotOut}}
    """
    v_result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = v_result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    # Fetch courts for metadata
    courts_result = await db.execute(
        select(Court)
        .where(Court.venue_id == venue_id, Court.is_active == True)  # noqa: E712
        .order_by(Court.sort_order)
    )
    courts = courts_result.scalars().all()

    # Redis dependency injected via app state in main.py
    from app.main import app

    redis: Redis = app.state.redis

    grid = await get_availability_grid(db, redis, venue_id, target_date)

    return AvailabilityResponse(
        courts=[
            CourtMeta(
                id=str(c.id),
                name=c.name,
                is_indoor=c.is_indoor,
                surface=c.surface,
                court_type_id=str(c.court_type_id) if c.court_type_id else None,
                sort_order=c.sort_order,
            )
            for c in courts
        ],
        slots={
            court_id: {
                slot_key: SlotOut(
                    court_id=slot.court_id,
                    slot_start=slot.slot_start,
                    slot_end=slot.slot_end,
                    status=slot.status,
                    amount_cents=slot.amount_cents,
                    original_amount_cents=slot.original_amount_cents,
                )
                for slot_key, slot in slots.items()
            }
            for court_id, slots in grid.items()
        },
    )
