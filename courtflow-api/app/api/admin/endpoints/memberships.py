from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.organization import MembershipTier, MembershipTierScope

router = APIRouter(prefix="/membership-tiers", tags=["admin-memberships"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class TierOut(BaseModel):
    id: str
    organization_id: str
    scope: str
    venue_id: str | None
    court_type_id: str | None
    court_id: str | None
    name: str
    description: str | None
    priority: int
    price_cents: int
    duration_days: int
    price_discount_pct: int
    booking_window_days: int
    monthly_hour_quota: int | None
    max_concurrent_bookings: int | None
    is_active: bool
    created_at: str
    updated_at: str


class TierCreate(BaseModel):
    scope: str = "organization"
    venue_id: str | None = None
    court_type_id: str | None = None
    court_id: str | None = None
    name: str
    description: str | None = None
    priority: int = 0
    price_cents: int = 0
    duration_days: int = 30
    price_discount_pct: int = 0
    booking_window_days: int = 7
    monthly_hour_quota: int | None = None
    max_concurrent_bookings: int | None = None


class TierUpdate(BaseModel):
    scope: str | None = None
    venue_id: str | None = None
    court_type_id: str | None = None
    court_id: str | None = None
    name: str | None = None
    description: str | None = None
    priority: int | None = None
    price_cents: int | None = None
    duration_days: int | None = None
    price_discount_pct: int | None = None
    booking_window_days: int | None = None
    monthly_hour_quota: int | None = None
    max_concurrent_bookings: int | None = None
    is_active: bool | None = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _tier_out(t: MembershipTier) -> TierOut:
    return TierOut(
        id=str(t.id),
        organization_id=str(t.organization_id),
        scope=t.scope.value,
        venue_id=str(t.venue_id) if t.venue_id else None,
        court_type_id=str(t.court_type_id) if t.court_type_id else None,
        court_id=str(t.court_id) if t.court_id else None,
        name=t.name,
        description=t.description,
        priority=t.priority,
        price_cents=t.price_cents,
        duration_days=t.duration_days,
        price_discount_pct=t.price_discount_pct,
        booking_window_days=t.booking_window_days,
        monthly_hour_quota=t.monthly_hour_quota,
        max_concurrent_bookings=t.max_concurrent_bookings,
        is_active=t.is_active,
        created_at=t.created_at.isoformat(),
        updated_at=t.updated_at.isoformat(),
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("", response_model=list[TierOut])
async def list_tiers(
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    result = await db.execute(
        select(MembershipTier)
        .where(MembershipTier.organization_id == member.organization_id)
        .order_by(MembershipTier.priority.desc())
    )
    return [_tier_out(t) for t in result.scalars().all()]


@router.post("", response_model=TierOut, status_code=201)
async def create_tier(
    body: TierCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    data = body.model_dump()
    data["scope"] = MembershipTierScope(data["scope"])
    tier = MembershipTier(organization_id=member.organization_id, **data)
    db.add(tier)
    await db.commit()
    await db.refresh(tier)
    return _tier_out(tier)


@router.get("/{tier_id}", response_model=TierOut)
async def get_tier(
    tier_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    result = await db.execute(
        select(MembershipTier).where(
            MembershipTier.id == tier_id,
            MembershipTier.organization_id == member.organization_id,
        )
    )
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="Membership tier not found")
    return _tier_out(tier)


@router.put("/{tier_id}", response_model=TierOut)
async def update_tier(
    tier_id: str,
    body: TierUpdate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    result = await db.execute(
        select(MembershipTier).where(
            MembershipTier.id == tier_id,
            MembershipTier.organization_id == member.organization_id,
        )
    )
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="Membership tier not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        if field == "scope" and isinstance(value, str):
            value = MembershipTierScope(value)
        setattr(tier, field, value)

    await db.commit()
    await db.refresh(tier)
    return _tier_out(tier)


@router.delete("/{tier_id}", status_code=204)
async def delete_tier(
    tier_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    result = await db.execute(
        select(MembershipTier).where(
            MembershipTier.id == tier_id,
            MembershipTier.organization_id == member.organization_id,
        )
    )
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="Membership tier not found")
    await db.delete(tier)
    await db.commit()
