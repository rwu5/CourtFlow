import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class PlayerLevel(str, enum.Enum):
    beginner = "beginner"  # 新手
    elementary = "elementary"  # 初级
    intermediate = "intermediate"  # 中级
    advanced = "advanced"  # 高级
    professional = "professional"  # 专业


class DominantHand(str, enum.Enum):
    left = "left"
    right = "right"


class BackhandType(str, enum.Enum):
    two_handed = "two_handed"  # 双手反手
    one_handed = "one_handed"  # 单手反手


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    wechat_openid: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True
    )
    wechat_unionid: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(String(200), nullable=True)
    gender: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # male / female
    birthday: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    email: Mapped[str | None] = mapped_column(String(254), unique=True, nullable=True)
    player_level: Mapped[PlayerLevel] = mapped_column(
        SAEnum(PlayerLevel), default=PlayerLevel.beginner
    )
    dominant_hand: Mapped[DominantHand | None] = mapped_column(
        SAEnum(DominantHand), nullable=True
    )
    backhand_type: Mapped[BackhandType | None] = mapped_column(
        SAEnum(BackhandType), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    org_memberships: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="user"
    )  # noqa: F821
    memberships: Mapped[list["UserMembership"]] = relationship(  # noqa: F821
        back_populates="user"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
