from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.venue import Venue
from app.models.court import Court, CourtType, CourtMedia

router = APIRouter(tags=["admin-courts"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class CourtOut(BaseModel):
    id: str
    venue_id: str
    court_type_id: str | None
    name: str
    surface: str | None
    is_indoor: bool
    slot_duration_minutes: int
    sort_order: int
    is_active: bool
    created_at: str


class CourtCreate(BaseModel):
    court_type_id: str | None = None
    name: str
    surface: str | None = None
    is_indoor: bool = True
    slot_duration_minutes: int = 60
    sort_order: int = 0


class CourtUpdate(BaseModel):
    court_type_id: str | None = None
    name: str | None = None
    surface: str | None = None
    is_indoor: bool | None = None
    slot_duration_minutes: int | None = None
    sort_order: int | None = None


class CourtTypeOut(BaseModel):
    id: str
    venue_id: str
    name: str
    description: str | None
    icon: str | None
    sort_order: int


class CourtMediaOut(BaseModel):
    id: str
    court_id: str
    url: str
    media_type: str
    sort_order: int


class CourtMediaCreate(BaseModel):
    url: str
    media_type: str = "photo"
    sort_order: int = 0


class CourtTypeCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    sort_order: int = 0


class CourtTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    sort_order: int | None = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _verify_venue(db, venue_id: str, org_id) -> Venue:
    result = await db.execute(
        select(Venue).where(Venue.id == venue_id, Venue.organization_id == org_id)
    )
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue


def _court_out(c: Court) -> CourtOut:
    return CourtOut(
        id=str(c.id),
        venue_id=str(c.venue_id),
        court_type_id=str(c.court_type_id) if c.court_type_id else None,
        name=c.name,
        surface=c.surface,
        is_indoor=c.is_indoor,
        slot_duration_minutes=c.slot_duration_minutes,
        sort_order=c.sort_order,
        is_active=c.is_active,
        created_at=c.created_at.isoformat(),
    )


# ─── Court CRUD ──────────────────────────────────────────────────────────────

@router.get("/venues/{venue_id}/courts", response_model=list[CourtOut])
async def list_courts(
    venue_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(Court).where(Court.venue_id == venue_id).order_by(Court.sort_order)
    )
    return [_court_out(c) for c in result.scalars().all()]


@router.post("/venues/{venue_id}/courts", response_model=CourtOut, status_code=201)
async def create_court(
    venue_id: str,
    body: CourtCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    court = Court(venue_id=venue_id, **body.model_dump())
    db.add(court)
    await db.commit()
    await db.refresh(court)
    return _court_out(court)


@router.get("/venues/{venue_id}/courts/{court_id}", response_model=CourtOut)
async def get_court(
    venue_id: str,
    court_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(Court).where(Court.id == court_id, Court.venue_id == venue_id)
    )
    court = result.scalar_one_or_none()
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")
    return _court_out(court)


@router.put("/venues/{venue_id}/courts/{court_id}", response_model=CourtOut)
async def update_court(
    venue_id: str,
    court_id: str,
    body: CourtUpdate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(Court).where(Court.id == court_id, Court.venue_id == venue_id)
    )
    court = result.scalar_one_or_none()
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(court, field, value)

    await db.commit()
    await db.refresh(court)
    return _court_out(court)


@router.delete("/venues/{venue_id}/courts/{court_id}", status_code=204)
async def delete_court(
    venue_id: str,
    court_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(Court).where(Court.id == court_id, Court.venue_id == venue_id)
    )
    court = result.scalar_one_or_none()
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")
    court.is_active = False
    await db.commit()


# ─── Court Types ─────────────────────────────────────────────────────────────

@router.get("/venues/{venue_id}/court-types", response_model=list[CourtTypeOut])
async def list_court_types(
    venue_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(CourtType).where(CourtType.venue_id == venue_id).order_by(CourtType.sort_order)
    )
    return [
        CourtTypeOut(
            id=str(ct.id), venue_id=str(ct.venue_id), name=ct.name,
            description=ct.description, icon=ct.icon, sort_order=ct.sort_order,
        )
        for ct in result.scalars().all()
    ]


@router.post("/venues/{venue_id}/court-types", response_model=CourtTypeOut, status_code=201)
async def create_court_type(
    venue_id: str,
    body: CourtTypeCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    ct = CourtType(venue_id=venue_id, **body.model_dump())
    db.add(ct)
    await db.commit()
    await db.refresh(ct)
    return CourtTypeOut(
        id=str(ct.id), venue_id=str(ct.venue_id), name=ct.name,
        description=ct.description, icon=ct.icon, sort_order=ct.sort_order,
    )


@router.put("/venues/{venue_id}/court-types/{type_id}", response_model=CourtTypeOut)
async def update_court_type(
    venue_id: str,
    type_id: str,
    body: CourtTypeUpdate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(CourtType).where(CourtType.id == type_id, CourtType.venue_id == venue_id)
    )
    ct = result.scalar_one_or_none()
    if not ct:
        raise HTTPException(status_code=404, detail="Court type not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(ct, field, value)

    await db.commit()
    await db.refresh(ct)
    return CourtTypeOut(
        id=str(ct.id), venue_id=str(ct.venue_id), name=ct.name,
        description=ct.description, icon=ct.icon, sort_order=ct.sort_order,
    )


@router.delete("/venues/{venue_id}/court-types/{type_id}", status_code=204)
async def delete_court_type(
    venue_id: str,
    type_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(CourtType).where(CourtType.id == type_id, CourtType.venue_id == venue_id)
    )
    ct = result.scalar_one_or_none()
    if not ct:
        raise HTTPException(status_code=404, detail="Court type not found")
    await db.delete(ct)
    await db.commit()


# ─── Court Media ────────────────────────────────────────────────────────────

@router.get("/venues/{venue_id}/courts/{court_id}/media", response_model=list[CourtMediaOut])
async def list_court_media(
    venue_id: str,
    court_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(CourtMedia)
        .where(CourtMedia.court_id == court_id)
        .order_by(CourtMedia.sort_order)
    )
    return [
        CourtMediaOut(
            id=str(m.id), court_id=str(m.court_id), url=m.url,
            media_type=m.media_type, sort_order=m.sort_order,
        )
        for m in result.scalars().all()
    ]


@router.post("/venues/{venue_id}/courts/{court_id}/media", response_model=CourtMediaOut, status_code=201)
async def create_court_media(
    venue_id: str,
    court_id: str,
    body: CourtMediaCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    # Verify court exists
    result = await db.execute(
        select(Court).where(Court.id == court_id, Court.venue_id == venue_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Court not found")

    media = CourtMedia(court_id=court_id, **body.model_dump())
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return CourtMediaOut(
        id=str(media.id), court_id=str(media.court_id), url=media.url,
        media_type=media.media_type, sort_order=media.sort_order,
    )


@router.delete("/venues/{venue_id}/courts/{court_id}/media/{media_id}", status_code=204)
async def delete_court_media(
    venue_id: str,
    court_id: str,
    media_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(CourtMedia).where(CourtMedia.id == media_id, CourtMedia.court_id == court_id)
    )
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    await db.delete(media)
    await db.commit()
