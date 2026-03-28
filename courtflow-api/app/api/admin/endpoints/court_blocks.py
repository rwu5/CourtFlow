from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.venue import Venue
from app.models.court import Court, CourtBlock

router = APIRouter(tags=["admin-court-blocks"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class CourtBlockOut(BaseModel):
    id: str
    court_id: str
    start_at: str
    end_at: str
    reason: str | None
    created_by: str | None
    created_at: str


class CourtBlockCreate(BaseModel):
    start_at: str
    end_at: str
    reason: str | None = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _verify_venue(db, venue_id: str, org_id) -> Venue:
    result = await db.execute(
        select(Venue).where(Venue.id == venue_id, Venue.organization_id == org_id)
    )
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue


def _block_out(b: CourtBlock) -> CourtBlockOut:
    return CourtBlockOut(
        id=str(b.id),
        court_id=str(b.court_id),
        start_at=b.start_at.isoformat(),
        end_at=b.end_at.isoformat(),
        reason=b.reason,
        created_by=str(b.created_by) if b.created_by else None,
        created_at=b.created_at.isoformat(),
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get(
    "/venues/{venue_id}/courts/{court_id}/blocks",
    response_model=list[CourtBlockOut],
)
async def list_court_blocks(
    venue_id: str,
    court_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(CourtBlock)
        .where(CourtBlock.court_id == court_id)
        .order_by(CourtBlock.start_at.desc())
    )
    return [_block_out(b) for b in result.scalars().all()]


@router.post(
    "/venues/{venue_id}/courts/{court_id}/blocks",
    response_model=CourtBlockOut,
    status_code=201,
)
async def create_court_block(
    venue_id: str,
    court_id: str,
    body: CourtBlockCreate,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user, member = admin
    await _verify_venue(db, venue_id, member.organization_id)

    # Verify court belongs to venue
    result = await db.execute(
        select(Court).where(Court.id == court_id, Court.venue_id == venue_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Court not found")

    from datetime import datetime
    block = CourtBlock(
        court_id=court_id,
        start_at=datetime.fromisoformat(body.start_at),
        end_at=datetime.fromisoformat(body.end_at),
        reason=body.reason,
        created_by=user.id,
    )
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return _block_out(block)


@router.delete(
    "/venues/{venue_id}/courts/{court_id}/blocks/{block_id}",
    status_code=204,
)
async def delete_court_block(
    venue_id: str,
    court_id: str,
    block_id: str,
    admin: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    _, member = admin
    await _verify_venue(db, venue_id, member.organization_id)
    result = await db.execute(
        select(CourtBlock).where(
            CourtBlock.id == block_id, CourtBlock.court_id == court_id
        )
    )
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Court block not found")
    await db.delete(block)
    await db.commit()
