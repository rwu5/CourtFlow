"""Development seed: creates one org, one venue, 3 courts, pricing rules, and a test user.

Run with:  python -m seeds.seed_dev
"""

import asyncio
import uuid
from datetime import time

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.organization import Organization, MembershipTier
from app.models.venue import Venue, VenueFacility
from app.models.court import Court, CourtType
from app.models.pricing import PricingRule
from app.models.user import User


async def seed():
    engine = create_async_engine(settings.database_url, echo=True)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as db:
        # Organization
        org = Organization(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            name="瑛赛网球",
            slug="insighttennis",
            is_partner=False,
        )
        db.add(org)

        # Venue
        venue = Venue(
            id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
            organization_id=org.id,
            name="瑛赛AI网球学练馆（陆家嘴尚悦湾店）",
            short_name="陆家嘴店",
            address="上海市浦东新区银城路66号尚悦湾广场L204",
            city="上海",
            district="浦东新区",
            latitude=31.2350,
            longitude=121.5000,
            timezone="Asia/Shanghai",
            phone="021-12345678",
            open_time="07:00",
            close_time="22:00",
            slot_duration_minutes=60,
        )
        db.add(venue)

        # Facility tags
        for key, label in [
            ("high_ceiling", "高楼层球场"),
            ("wide_training", "加宽学练场"),
            ("basic_training", "基础学练场"),
            ("mid_training", "中面训练场"),
        ]:
            db.add(VenueFacility(venue_id=venue.id, key=key, label=label))

        # Court type
        ct_standard = CourtType(
            id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
            venue_id=venue.id,
            name="标准场",
            sort_order=0,
        )
        db.add(ct_standard)

        # Courts
        for i, name in enumerate(["场地01", "场地02", "场地03"]):
            db.add(
                Court(
                    id=uuid.UUID(f"00000000-0000-0000-0000-{str(i+1).zfill(12)}"),
                    venue_id=venue.id,
                    court_type_id=ct_standard.id,
                    name=name,
                    surface="hard",
                    is_indoor=True,
                    sort_order=i,
                )
            )

        # Pricing rules (mirrors the screenshots: ¥88–¥148 depending on time/court)
        rules = [
            # Peak hours (10:00–22:00, weekdays) — Court 01 (场地01 is pricier)
            PricingRule(
                venue_id=venue.id,
                court_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                name="场地01 高峰工作日",
                priority=20,
                weekdays="0,1,2,3,4",
                time_from=time(10, 0),
                time_to=time(22, 0),
                amount_cents=14800,
                original_amount_cents=20800,
            ),
            # Off-peak (07:00–10:00, weekdays) — Court 01
            PricingRule(
                venue_id=venue.id,
                court_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                name="场地01 低峰工作日",
                priority=15,
                weekdays="0,1,2,3,4",
                time_from=time(7, 0),
                time_to=time(10, 0),
                amount_cents=11800,
                original_amount_cents=16800,
            ),
            # Courts 02+03 default (weekday)
            PricingRule(
                venue_id=venue.id,
                name="标准场 高峰工作日",
                priority=10,
                weekdays="0,1,2,3,4",
                time_from=time(10, 0),
                time_to=time(22, 0),
                amount_cents=12800,
                original_amount_cents=18800,
            ),
            PricingRule(
                venue_id=venue.id,
                name="标准场 低峰工作日",
                priority=9,
                weekdays="0,1,2,3,4",
                time_from=time(7, 0),
                time_to=time(10, 0),
                amount_cents=9800,
                original_amount_cents=14800,
            ),
            # Weekend — all courts
            PricingRule(
                venue_id=venue.id,
                name="周末高峰",
                priority=5,
                weekdays="5,6",
                time_from=time(10, 0),
                time_to=time(22, 0),
                amount_cents=16800,
                original_amount_cents=22800,
            ),
        ]
        for r in rules:
            db.add(r)

        # Test user
        user = User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000099"),
            wechat_openid="dev_openid_test",
            phone="19195233697",
            nickname="瑛赛网球用户3697",
        )
        db.add(user)

        await db.commit()
        print("✅ Seed complete")


if __name__ == "__main__":
    asyncio.run(seed())
