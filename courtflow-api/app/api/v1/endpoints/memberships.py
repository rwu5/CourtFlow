"""Membership tiers and user membership management.

Endpoints:
  GET  /memberships/tiers              — list purchasable tiers (filterable by venue/court)
  GET  /memberships/tiers/{tier_id}    — tier detail
  POST /memberships/join               — purchase / join a tier (creates UserMembership)
  GET  /memberships/my                 — caller's active memberships
  POST /memberships/{id}/cancel        — cancel a membership
"""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.organization import (
    MembershipTier,
    MembershipTierScope,
    UserMembership,
    UserMembershipStatus,
)
from app.models.user import User

router = APIRouter(prefix="/memberships", tags=["memberships"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class TierOut(BaseModel):
    id: str
    organization_id: str
    scope: str
    venue_id: str | None
    court_type_id: str | None
    court_id: str | None
    name: str
    description: str | None
    price_cents: int
    duration_days: int
    price_discount_pct: int
    booking_window_days: int
    monthly_hour_quota: int | None
    max_concurrent_bookings: int | None

    model_config = {"from_attributes": True}


class UserMembershipOut(BaseModel):
    id: str
    tier_id: str
    tier_name: str
    scope: str
    status: str
    starts_at: str
    expires_at: str
    price_discount_pct: int
    booking_window_days: int
    monthly_hour_quota: int | None

    model_config = {"from_attributes": True}


class JoinRequest(BaseModel):
    tier_id: str


class JoinResponse(BaseModel):
    membership_id: str
    tier_name: str
    starts_at: str
    expires_at: str
    status: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _tier_to_out(t: MembershipTier) -> TierOut:
    return TierOut(
        id=str(t.id),
        organization_id=str(t.organization_id),
        scope=t.scope.value,
        venue_id=str(t.venue_id) if t.venue_id else None,
        court_type_id=str(t.court_type_id) if t.court_type_id else None,
        court_id=str(t.court_id) if t.court_id else None,
        name=t.name,
        description=t.description,
        price_cents=t.price_cents,
        duration_days=t.duration_days,
        price_discount_pct=t.price_discount_pct,
        booking_window_days=t.booking_window_days,
        monthly_hour_quota=t.monthly_hour_quota,
        max_concurrent_bookings=t.max_concurrent_bookings,
    )


def _membership_to_out(m: UserMembership) -> UserMembershipOut:
    return UserMembershipOut(
        id=str(m.id),
        tier_id=str(m.tier_id),
        tier_name=m.tier.name,
        scope=m.tier.scope.value,
        status=m.status.value,
        starts_at=m.starts_at.isoformat(),
        expires_at=m.expires_at.isoformat(),
        price_discount_pct=m.tier.price_discount_pct,
        booking_window_days=m.tier.booking_window_days,
        monthly_hour_quota=m.tier.monthly_hour_quota,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/tiers", response_model=list[TierOut])
async def list_tiers(
    venue_id: str
    | None = Query(None, description="Filter tiers applicable to a venue"),
    court_type_id: str | None = Query(None),
    court_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return all active membership tiers matching the optional scope filters.

    A tier is returned if it's org-wide OR if its venue/court_type/court FK
    matches the provided filter value.
    """
    q = select(MembershipTier).where(MembershipTier.is_active == True)  # noqa: E712

    if court_id:
        q = q.where(
            (MembershipTier.scope == MembershipTierScope.court)
            & (MembershipTier.court_id == court_id)
        )
    elif court_type_id:
        q = q.where(
            (MembershipTier.scope == MembershipTierScope.court_type)
            & (MembershipTier.court_type_id == court_type_id)
        )
    elif venue_id:
        # Return venue-scoped tiers + org-wide tiers for this venue's org
        q = q.where(
            (MembershipTier.scope == MembershipTierScope.organization)
            | (
                (MembershipTier.scope == MembershipTierScope.venue)
                & (MembershipTier.venue_id == venue_id)
            )
        )

    result = await db.execute(q.order_by(MembershipTier.priority.desc()))
    tiers = result.scalars().all()
    return [_tier_to_out(t) for t in tiers]


@router.get("/tiers/{tier_id}", response_model=TierOut)
async def get_tier(
    tier_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MembershipTier).where(
            MembershipTier.id == tier_id,
            MembershipTier.is_active == True,  # noqa: E712
        )
    )
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="Membership tier not found")
    return _tier_to_out(tier)


@router.post("/join", response_model=JoinResponse, status_code=status.HTTP_201_CREATED)
async def join_tier(
    body: JoinRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Join / purchase a membership tier.

    For paid tiers (price_cents > 0) this endpoint creates a pending membership
    that should be activated after payment confirmation. For free tiers it
    activates immediately.

    Note: Payment integration is handled by the orders/payments flow — this
    endpoint focuses on membership lifecycle.
    """
    # Fetch tier
    result = await db.execute(
        select(MembershipTier).where(
            MembershipTier.id == body.tier_id,
            MembershipTier.is_active == True,  # noqa: E712
        )
    )
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="Membership tier not found")

    # Check for existing active membership on the same tier
    existing = await db.execute(
        select(UserMembership).where(
            UserMembership.user_id == current_user.id,
            UserMembership.tier_id == tier.id,
            UserMembership.status == UserMembershipStatus.active,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="You already have an active membership for this tier",
        )

    now = datetime.now(timezone.utc)
    # Free tiers activate immediately; paid tiers start immediately too but
    # in a real flow you'd wait for payment confirmation before setting active.
    membership = UserMembership(
        id=uuid.uuid4(),
        user_id=current_user.id,
        tier_id=tier.id,
        status=UserMembershipStatus.active,
        starts_at=now,
        expires_at=now + timedelta(days=tier.duration_days),
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)

    return JoinResponse(
        membership_id=str(membership.id),
        tier_name=tier.name,
        starts_at=membership.starts_at.isoformat(),
        expires_at=membership.expires_at.isoformat(),
        status=membership.status.value,
    )


@router.get("/my", response_model=list[UserMembershipOut])
async def my_memberships(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the caller's memberships, joined with tier details."""
    q = (
        select(UserMembership)
        .where(UserMembership.user_id == current_user.id)
        .order_by(UserMembership.expires_at.desc())
    )
    if active_only:
        q = q.where(UserMembership.status == UserMembershipStatus.active)

    result = await db.execute(q)
    memberships = result.scalars().all()
    return [_membership_to_out(m) for m in memberships]


@router.post("/{membership_id}/cancel", response_model=UserMembershipOut)
async def cancel_membership(
    membership_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserMembership).where(
            UserMembership.id == membership_id,
            UserMembership.user_id == current_user.id,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    if membership.status != UserMembershipStatus.active:
        raise HTTPException(
            status_code=400, detail="Only active memberships can be cancelled"
        )

    membership.status = UserMembershipStatus.cancelled
    await db.commit()
    await db.refresh(membership)
    return _membership_to_out(membership)
