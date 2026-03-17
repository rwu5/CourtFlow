import uuid
from datetime import datetime
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum as SAEnum,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class OrgMemberRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    staff = "staff"
    coach = "coach"
    member = "member"


class MembershipTierScope(str, enum.Enum):
    organization = "organization"  # valid across all venues in org
    venue = "venue"  # valid at one venue only
    court_type = "court_type"  # valid for a specific court type
    court = "court"  # valid for a specific court


class UserMembershipStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    suspended = "suspended"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # partner = False means self-operated
    is_partner: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    venues: Mapped[list["Venue"]] = relationship(
        back_populates="organization"
    )  # noqa: F821
    membership_tiers: Mapped[list["MembershipTier"]] = relationship(
        back_populates="organization"
    )
    members: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="organization"
    )


class MembershipTier(Base):
    """Purchasable membership tier scoped to org / venue / court-type / court.

    When a user holds an active UserMembership for this tier, the pricing engine
    will apply price_discount_pct (or match a PricingRule keyed on membership_tier_id).
    """

    __tablename__ = "membership_tiers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    # Scope — only one of the three FK columns below should be set (per scope value)
    scope: Mapped[MembershipTierScope] = mapped_column(
        SAEnum(MembershipTierScope), default=MembershipTierScope.organization
    )
    venue_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=True
    )
    court_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("court_types.id"), nullable=True
    )
    court_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False)  # 月卡, 年卡, VIP
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    # Purchase price
    price_cents: Mapped[int] = mapped_column(Integer, default=0)  # 0 = free/invite-only
    duration_days: Mapped[int] = mapped_column(
        Integer, default=30
    )  # membership validity

    # Benefits
    price_discount_pct: Mapped[int] = mapped_column(Integer, default=0)  # 0–100
    booking_window_days: Mapped[int] = mapped_column(
        Integer, default=7
    )  # advance booking
    monthly_hour_quota: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # NULL = unlimited
    max_concurrent_bookings: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # NULL = unlimited

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="membership_tiers"
    )
    members: Mapped[list["OrganizationMember"]] = relationship(back_populates="tier")
    user_memberships: Mapped[list["UserMembership"]] = relationship(
        back_populates="tier"
    )


class UserMembership(Base):
    """An active (or historical) membership held by a user for a specific tier."""

    __tablename__ = "user_memberships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("membership_tiers.id"), nullable=False
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True
    )
    status: Mapped[UserMembershipStatus] = mapped_column(
        SAEnum(UserMembershipStatus), default=UserMembershipStatus.active
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    tier: Mapped["MembershipTier"] = relationship(back_populates="user_memberships")
    user: Mapped["User"] = relationship(back_populates="memberships")  # noqa: F821


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("membership_tiers.id"), nullable=True
    )
    role: Mapped[OrgMemberRole] = mapped_column(
        SAEnum(OrgMemberRole), default=OrgMemberRole.member
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    organization: Mapped["Organization"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="org_memberships")
    tier: Mapped["MembershipTier | None"] = relationship(back_populates="members")
