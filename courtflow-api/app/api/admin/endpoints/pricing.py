from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.venue import Venue
from app.models.pricing import PricingRule

router = APIRouter(prefix="/pricing-rules", tags=["admin-pricing"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class PricingRuleOut(BaseModel):
    id: str
    venue_id: str
    court_id: str | None
    court_type_id: str | None
    membership_tier_id: str | None
    name: str
    priority: int
    weekdays: str | None
    date_from: str | None
    date_to: str | None
    time_from: str | None
    time_to: str | None
    is_holiday: bool | None
    amount_cents: int
    original_amount_cents: int | None
    is_active: bool
    created_at: str
    updated_at: str


class PricingRuleCreate(BaseModel):
    venue_id: str
    court_id: str | None = None
    court_type_id: str | None = None
    membership_tier_id: str | None = None
    name: str
    priority: int = 0
    weekdays: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    time_from: str | None = None
    time_to: str | None = None
    is_holiday: bool | None = None
    amount_cents: int
    original_amount_cents: int | None = None


class PricingRuleUpdate(BaseModel):
    court_id: str | None = None
    court_type_id: str | None = None
    membership_tier_id: str | None = None
    name: str | None = None
    priority: int | None = None
    weekdays: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    time_from: str | None = None
    time_to: str | None = None
    is_holiday: bool | None = None
    amount_cents: int | None = None
    original_amount_cents: int | None = None
    is_active: bool | None = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _rule_out(r: PricingRule) -> PricingRuleOut:
    return PricingRuleOut(
        id=str(r.id),
        venue_id=str(r.venue_id),
        court_id=str(r.court_id) if r.court_id else None,
        court_type_id=str(r.court_type_id) if r.court_type_id else None,
        membership_tier_id=str(r.membership_tier_id) if r.membership_tier_id else None,
        name=r.name,
        priority=r.priority,
        weekdays=r.weekdays,
        date_from=r.date_from.isoformat() if r.date_from else None,
        date_to=r.date_to.isoformat() if r.date_to else None,
        time_from=r.time_from.isoformat() if r.time_from else None,
        time_to=r.time_to.isoformat() if r.time_to else None,
        is_holiday=r.is_holiday,
        amount_cents=r.amount_cents,
        original_amount_cents=r.original_amount_cents,
        is_active=r.is_active,
        created_at=r.created_at.isoformat(),
        updated_at=r.updated_at.isoformat(),
    )


async def _get_org_venue_ids(db, org_id) -> list:
    result = await db.execute(
        select(Venue.id).where(Venue.organization_id == org_id)
    )
    return [row[0] for row in result.all()]


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("", response_model=list[PricingRuleOut])
async def list_pricing_rules(
    venue_id: str | None = Query(None),
    court_id: str | None = Query(None),
    court_type_id: str | None = Query(None),
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)

    q = select(PricingRule).where(PricingRule.venue_id.in_(venue_ids))
    if venue_id:
        q = q.where(PricingRule.venue_id == venue_id)
    if court_id:
        q = q.where(PricingRule.court_id == court_id)
    if court_type_id:
        q = q.where(PricingRule.court_type_id == court_type_id)
    q = q.order_by(PricingRule.priority.desc())

    result = await db.execute(q)
    return [_rule_out(r) for r in result.scalars().all()]


@router.post("", response_model=PricingRuleOut, status_code=201)
async def create_pricing_rule(
    body: PricingRuleCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    if body.venue_id not in [str(vid) for vid in venue_ids]:
        raise HTTPException(status_code=403, detail="Venue not in your organization")

    from datetime import date, time

    data = body.model_dump()
    # Convert string dates/times to proper types
    for dt_field in ("date_from", "date_to"):
        if data[dt_field]:
            data[dt_field] = date.fromisoformat(data[dt_field])
    for t_field in ("time_from", "time_to"):
        if data[t_field]:
            data[t_field] = time.fromisoformat(data[t_field])

    rule = PricingRule(**data)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return _rule_out(rule)


@router.get("/{rule_id}", response_model=PricingRuleOut)
async def get_pricing_rule(
    rule_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    result = await db.execute(
        select(PricingRule).where(
            PricingRule.id == rule_id, PricingRule.venue_id.in_(venue_ids)
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    return _rule_out(rule)


@router.put("/{rule_id}", response_model=PricingRuleOut)
async def update_pricing_rule(
    rule_id: str,
    body: PricingRuleUpdate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    result = await db.execute(
        select(PricingRule).where(
            PricingRule.id == rule_id, PricingRule.venue_id.in_(venue_ids)
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")

    from datetime import date, time

    for field, value in body.model_dump(exclude_unset=True).items():
        if field in ("date_from", "date_to") and isinstance(value, str):
            value = date.fromisoformat(value)
        elif field in ("time_from", "time_to") and isinstance(value, str):
            value = time.fromisoformat(value)
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return _rule_out(rule)


@router.delete("/{rule_id}", status_code=204)
async def delete_pricing_rule(
    rule_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    venue_ids = await _get_org_venue_ids(db, member.organization_id)
    result = await db.execute(
        select(PricingRule).where(
            PricingRule.id == rule_id, PricingRule.venue_id.in_(venue_ids)
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    await db.delete(rule)
    await db.commit()
