from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.venue import Venue, VenueMedia, VenueFacility

router = APIRouter(prefix="/venues", tags=["admin-venues"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class VenueOut(BaseModel):
    id: str
    name: str
    short_name: str | None
    address: str
    city: str
    district: str | None
    latitude: float | None
    longitude: float | None
    timezone: str
    phone: str | None
    wechat_cs: str | None
    parking_info: str | None
    open_time: str
    close_time: str
    is_active: bool
    created_at: str
    updated_at: str


class VenueCreate(BaseModel):
    name: str
    short_name: str | None = None
    address: str
    city: str
    district: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str = "Asia/Shanghai"
    phone: str | None = None
    wechat_cs: str | None = None
    parking_info: str | None = None
    open_time: str = "07:00"
    close_time: str = "22:00"


class VenueUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    address: str | None = None
    city: str | None = None
    district: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    phone: str | None = None
    wechat_cs: str | None = None
    parking_info: str | None = None
    open_time: str | None = None
    close_time: str | None = None


class MediaOut(BaseModel):
    id: str
    url: str
    media_type: str
    sort_order: int


class MediaCreate(BaseModel):
    url: str
    media_type: str = "photo"
    sort_order: int = 0


class FacilityOut(BaseModel):
    id: str
    key: str
    label: str
    icon: str | None
    description: str | None


class FacilityCreate(BaseModel):
    key: str
    label: str
    icon: str | None = None
    description: str | None = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _venue_out(v: Venue) -> VenueOut:
    return VenueOut(
        id=str(v.id),
        name=v.name,
        short_name=v.short_name,
        address=v.address,
        city=v.city,
        district=v.district,
        latitude=float(v.latitude) if v.latitude else None,
        longitude=float(v.longitude) if v.longitude else None,
        timezone=v.timezone,
        phone=v.phone,
        wechat_cs=v.wechat_cs,
        parking_info=v.parking_info,
        open_time=v.open_time,
        close_time=v.close_time,
        is_active=v.is_active,
        created_at=v.created_at.isoformat(),
        updated_at=v.updated_at.isoformat(),
    )


async def _get_venue_for_org(db, venue_id: str, org_id) -> Venue:
    result = await db.execute(
        select(Venue).where(Venue.id == venue_id, Venue.organization_id == org_id)
    )
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue


# ─── Venue CRUD ──────────────────────────────────────────────────────────────

@router.get("", response_model=list[VenueOut])
async def list_venues(
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    result = await db.execute(
        select(Venue)
        .where(Venue.organization_id == member.organization_id)
        .order_by(Venue.created_at)
    )
    return [_venue_out(v) for v in result.scalars().all()]


@router.post("", response_model=VenueOut, status_code=201)
async def create_venue(
    body: VenueCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue = Venue(organization_id=member.organization_id, **body.model_dump())
    db.add(venue)
    await db.commit()
    await db.refresh(venue)
    return _venue_out(venue)


@router.get("/{venue_id}", response_model=VenueOut)
async def get_venue(
    venue_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue = await _get_venue_for_org(db, venue_id, member.organization_id)
    return _venue_out(venue)


@router.put("/{venue_id}", response_model=VenueOut)
async def update_venue(
    venue_id: str,
    body: VenueUpdate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue = await _get_venue_for_org(db, venue_id, member.organization_id)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(venue, field, value)

    await db.commit()
    await db.refresh(venue)
    return _venue_out(venue)


@router.delete("/{venue_id}", status_code=204)
async def delete_venue(
    venue_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue = await _get_venue_for_org(db, venue_id, member.organization_id)
    venue.is_active = False
    await db.commit()


# ─── Media ───────────────────────────────────────────────────────────────────

@router.get("/{venue_id}/media", response_model=list[MediaOut])
async def list_media(
    venue_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _get_venue_for_org(db, venue_id, member.organization_id)
    result = await db.execute(
        select(VenueMedia)
        .where(VenueMedia.venue_id == venue_id)
        .order_by(VenueMedia.sort_order)
    )
    return [
        MediaOut(id=str(m.id), url=m.url, media_type=m.media_type, sort_order=m.sort_order)
        for m in result.scalars().all()
    ]


@router.post("/{venue_id}/media", response_model=MediaOut, status_code=201)
async def create_media(
    venue_id: str,
    body: MediaCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _get_venue_for_org(db, venue_id, member.organization_id)
    media = VenueMedia(venue_id=venue_id, **body.model_dump())
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return MediaOut(id=str(media.id), url=media.url, media_type=media.media_type, sort_order=media.sort_order)


@router.delete("/{venue_id}/media/{media_id}", status_code=204)
async def delete_media(
    venue_id: str,
    media_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _get_venue_for_org(db, venue_id, member.organization_id)
    result = await db.execute(
        select(VenueMedia).where(VenueMedia.id == media_id, VenueMedia.venue_id == venue_id)
    )
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    await db.delete(media)
    await db.commit()


# ─── Facilities ──────────────────────────────────────────────────────────────

@router.get("/{venue_id}/facilities", response_model=list[FacilityOut])
async def list_facilities(
    venue_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _get_venue_for_org(db, venue_id, member.organization_id)
    result = await db.execute(
        select(VenueFacility).where(VenueFacility.venue_id == venue_id)
    )
    return [
        FacilityOut(id=str(f.id), key=f.key, label=f.label, icon=f.icon, description=f.description)
        for f in result.scalars().all()
    ]


@router.post("/{venue_id}/facilities", response_model=FacilityOut, status_code=201)
async def create_facility(
    venue_id: str,
    body: FacilityCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _get_venue_for_org(db, venue_id, member.organization_id)
    facility = VenueFacility(venue_id=venue_id, **body.model_dump())
    db.add(facility)
    await db.commit()
    await db.refresh(facility)
    return FacilityOut(id=str(facility.id), key=facility.key, label=facility.label, icon=facility.icon, description=facility.description)


@router.delete("/{venue_id}/facilities/{facility_id}", status_code=204)
async def delete_facility(
    venue_id: str,
    facility_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _get_venue_for_org(db, venue_id, member.organization_id)
    result = await db.execute(
        select(VenueFacility).where(VenueFacility.id == facility_id, VenueFacility.venue_id == venue_id)
    )
    facility = result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    await db.delete(facility)
    await db.commit()
