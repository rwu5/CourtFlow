"""Pricing engine — resolves the price for a court slot.

Rules are evaluated in descending priority order; first match wins.
Prices are stored and returned in fen (Chinese cents, 1 yuan = 100 fen).
"""

from datetime import datetime, date, time
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.court import Court
from app.models.pricing import PricingRule
from app.models.venue import Venue


async def resolve_price(
    db: AsyncSession,
    court: Court,
    slot_start: datetime,  # UTC
    membership_tier_id: str | None = None,
) -> tuple[int, int | None]:
    """Return (amount_cents, original_amount_cents) for the given slot.

    original_amount_cents is None if no strikethrough price applies.
    Raises ValueError if no matching rule found.
    """
    venue_result = await db.execute(select(Venue).where(Venue.id == court.venue_id))
    venue = venue_result.scalar_one()

    tz = ZoneInfo(venue.timezone)
    local_dt = slot_start.astimezone(tz)
    local_date: date = local_dt.date()
    local_time: time = local_dt.time()
    weekday = local_date.weekday()  # 0=Monday … 6=Sunday

    # Load all active rules for this venue, ordered by priority desc
    rules_result = await db.execute(
        select(PricingRule)
        .where(
            PricingRule.venue_id == venue.id,
            PricingRule.is_active == True,  # noqa: E712
        )
        .order_by(PricingRule.priority.desc())
    )
    rules = rules_result.scalars().all()

    for rule in rules:
        if not _rule_matches(
            rule, court, local_date, local_time, weekday, membership_tier_id
        ):
            continue
        return rule.amount_cents, rule.original_amount_cents

    raise ValueError(
        f"No pricing rule found for court {court.id} at {slot_start.isoformat()}"
    )


def _rule_matches(
    rule: PricingRule,
    court: Court,
    local_date: date,
    local_time: time,
    weekday: int,
    membership_tier_id: str | None,
) -> bool:
    # Court filter
    if rule.court_id is not None and str(rule.court_id) != str(court.id):
        return False
    if rule.court_type_id is not None and str(rule.court_type_id) != str(
        court.court_type_id
    ):
        return False

    # Membership tier filter
    if rule.membership_tier_id is not None:
        if str(rule.membership_tier_id) != membership_tier_id:
            return False

    # Date range
    if rule.date_from and local_date < rule.date_from:
        return False
    if rule.date_to and local_date > rule.date_to:
        return False

    # Weekday filter
    if rule.weekdays is not None:
        allowed = [int(d) for d in rule.weekdays.split(",") if d.strip()]
        if weekday not in allowed:
            return False

    # Time band
    if rule.time_from is not None and local_time < rule.time_from:
        return False
    if rule.time_to is not None and local_time >= rule.time_to:
        return False

    return True
