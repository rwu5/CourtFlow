from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, PlayerLevel, DominantHand, BackhandType

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileResponse(BaseModel):
    id: str
    nickname: str | None
    phone: str | None
    avatar_url: str | None
    bio: str | None
    gender: str | None
    player_level: str
    dominant_hand: str | None
    backhand_type: str | None

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    gender: str | None = None
    player_level: PlayerLevel | None = None
    dominant_hand: DominantHand | None = None
    backhand_type: BackhandType | None = None


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserProfileResponse)
async def update_me(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user
