"""WeChat Mini Program auth endpoints.

Flow:
  1. Client calls wx.login() → gets code
  2. POST /auth/wechat-login with code → server exchanges code for openid/session_key
  3. Server returns access_token + refresh_token
  4. Client optionally calls POST /auth/bind-phone with encrypted phone number
"""

from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from app.models.user import User, RefreshToken

router = APIRouter(prefix="/auth", tags=["auth"])


class WechatLoginRequest(BaseModel):
    code: str


class BindPhoneRequest(BaseModel):
    encrypted_data: str
    iv: str
    # OR plain phone for non-miniprogram channels
    phone: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    is_new_user: bool


class RefreshRequest(BaseModel):
    refresh_token: str


class PhoneLoginRequest(BaseModel):
    phone: str
    code: str


@router.post("/phone-login", response_model=TokenResponse)
async def phone_login(body: PhoneLoginRequest, db: AsyncSession = Depends(get_db)):
    """Phone + SMS code login for admin app.

    In development mode, any code is accepted.
    """
    if settings.app_env != "development":
        # TODO: integrate real SMS verification (e.g. Alibaba Cloud SMS)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SMS verification not configured",
        )

    result = await db.execute(select(User).where(User.phone == body.phone))
    user = result.scalar_one_or_none()
    is_new = user is None

    if not user:
        user = User(phone=body.phone, nickname=f"用户{body.phone[-4:]}")
        db.add(user)
        await db.flush()

    return await _issue_tokens(db, user, is_new)


@router.post("/wechat-login", response_model=TokenResponse)
async def wechat_login(body: WechatLoginRequest, db: AsyncSession = Depends(get_db)):
    """Exchange WeChat login code for CourtFlow access token."""
    openid, unionid = await _exchange_wechat_code(body.code)

    # Find or create user
    result = await db.execute(select(User).where(User.wechat_openid == openid))
    user = result.scalar_one_or_none()
    is_new = user is None

    if not user:
        user = User(wechat_openid=openid, wechat_unionid=unionid)
        db.add(user)
        await db.flush()

    return await _issue_tokens(db, user, is_new)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_refresh_token(body.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    stored = result.scalar_one_or_none()
    if not stored or stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    stored.revoked = True
    user_result = await db.execute(select(User).where(User.id == stored.user_id))
    user = user_result.scalar_one()
    return await _issue_tokens(db, user, False)


async def _exchange_wechat_code(code: str) -> tuple[str, str | None]:
    if settings.app_env == "development" and not settings.wechat_app_id:
        # Dev stub — use code as openid
        return f"dev_openid_{code}", None

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": settings.wechat_app_id,
                "secret": settings.wechat_app_secret,
                "js_code": code,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
    data = resp.json()
    if "errcode" in data and data["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"WeChat error: {data.get('errmsg', 'unknown')}",
        )
    return data["openid"], data.get("unionid")


async def _issue_tokens(db: AsyncSession, user: User, is_new: bool) -> TokenResponse:
    access_token = create_access_token(str(user.id))
    raw_refresh, hashed_refresh = create_refresh_token()

    rt = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expiry_days),
    )
    db.add(rt)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        user_id=str(user.id),
        is_new_user=is_new,
    )
