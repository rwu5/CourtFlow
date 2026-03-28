from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.organization import Organization, OrganizationMember, MembershipTier
from app.models.venue import Venue
from app.models.court import Court
from app.models.pricing import PricingRule
from app.models.user import User

router = APIRouter(tags=["admin-organization"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class OrganizationOut(BaseModel):
    id: str
    name: str
    slug: str
    logo_url: str | None
    description: str | None
    is_active: bool
    is_partner: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class OrganizationUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    logo_url: str | None = None
    description: str | None = None


class MemberOut(BaseModel):
    id: str
    user_id: str
    role: str
    is_active: bool
    joined_at: str
    nickname: str | None = None
    phone: str | None = None
    avatar_url: str | None = None


class DashboardStatsOut(BaseModel):
    total_venues: int
    total_courts: int
    total_members: int
    active_pricing_rules: int
    active_tiers: int


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/organization", response_model=OrganizationOut)
async def get_organization(
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user, member = admin
    result = await db.execute(
        select(Organization).where(Organization.id == member.organization_id)
    )
    org = result.scalar_one()
    return OrganizationOut(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        description=org.description,
        is_active=org.is_active,
        is_partner=org.is_partner,
        created_at=org.created_at.isoformat(),
        updated_at=org.updated_at.isoformat(),
    )


@router.put("/organization", response_model=OrganizationOut)
async def update_organization(
    body: OrganizationUpdate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user, member = admin
    result = await db.execute(
        select(Organization).where(Organization.id == member.organization_id)
    )
    org = result.scalar_one()

    if body.name is not None:
        org.name = body.name
    if body.slug is not None:
        org.slug = body.slug
    if body.logo_url is not None:
        org.logo_url = body.logo_url
    if body.description is not None:
        org.description = body.description

    await db.commit()
    await db.refresh(org)

    return OrganizationOut(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        description=org.description,
        is_active=org.is_active,
        is_partner=org.is_partner,
        created_at=org.created_at.isoformat(),
        updated_at=org.updated_at.isoformat(),
    )


@router.get("/organization/members", response_model=list[MemberOut])
async def list_members(
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user, member = admin
    result = await db.execute(
        select(OrganizationMember, User)
        .join(User, OrganizationMember.user_id == User.id)
        .where(OrganizationMember.organization_id == member.organization_id)
        .order_by(OrganizationMember.joined_at)
    )
    rows = result.all()
    return [
        MemberOut(
            id=str(m.id),
            user_id=str(m.user_id),
            role=m.role.value,
            is_active=m.is_active,
            joined_at=m.joined_at.isoformat(),
            nickname=u.nickname,
            phone=u.phone,
            avatar_url=u.avatar_url,
        )
        for m, u in rows
    ]


@router.get("/dashboard/stats", response_model=DashboardStatsOut)
async def get_dashboard_stats(
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user, member = admin
    org_id = member.organization_id

    venue_ids_q = select(Venue.id).where(Venue.organization_id == org_id)

    venues = (await db.execute(
        select(func.count()).select_from(Venue).where(
            Venue.organization_id == org_id, Venue.is_active == True  # noqa: E712
        )
    )).scalar_one()

    courts = (await db.execute(
        select(func.count()).select_from(Court).where(
            Court.venue_id.in_(venue_ids_q), Court.is_active == True  # noqa: E712
        )
    )).scalar_one()

    members = (await db.execute(
        select(func.count()).select_from(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    )).scalar_one()

    pricing_rules = (await db.execute(
        select(func.count()).select_from(PricingRule).where(
            PricingRule.venue_id.in_(venue_ids_q),
            PricingRule.is_active == True,  # noqa: E712
        )
    )).scalar_one()

    tiers = (await db.execute(
        select(func.count()).select_from(MembershipTier).where(
            MembershipTier.organization_id == org_id,
            MembershipTier.is_active == True,  # noqa: E712
        )
    )).scalar_one()

    return DashboardStatsOut(
        total_venues=venues,
        total_courts=courts,
        total_members=members,
        active_pricing_rules=pricing_rules,
        active_tiers=tiers,
    )
