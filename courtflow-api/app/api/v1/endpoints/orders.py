"""Order creation, retrieval, and cancellation."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.order import Order, OrderItem, OrderStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["orders"])


class CreateOrderRequest(BaseModel):
    reservation_ids: list[str]
    contact_phone: str | None = None


class OrderItemOut(BaseModel):
    item_type: str
    description: str
    quantity: int
    unit_price_cents: int
    total_cents: int


class OrderOut(BaseModel):
    id: str
    status: str
    subtotal_cents: int
    discount_cents: int
    total_cents: int
    contact_phone: str | None
    items: list[OrderItemOut]
    created_at: str


@router.post("", response_model=OrderOut)
async def create_order(
    body: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Convert a set of held reservations into a payable order."""
    res_ids = [uuid.UUID(r) for r in body.reservation_ids]

    result = await db.execute(
        select(Reservation).where(
            Reservation.id.in_(res_ids),
            Reservation.user_id == current_user.id,
            Reservation.status == ReservationStatus.held,
        )
    )
    reservations = result.scalars().all()

    if len(reservations) != len(res_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more reservations not found or not in held state",
        )

    # Check hold expiry
    now = datetime.now(timezone.utc)
    for res in reservations:
        if res.hold_expires_at and res.hold_expires_at < now:
            raise HTTPException(
                status_code=409, detail=f"Hold expired for reservation {res.id}"
            )

    # Build order
    subtotal = sum(r.amount_cents for r in reservations)
    venue_id = reservations[0].court.venue_id  # assume same venue

    order = Order(
        user_id=current_user.id,
        venue_id=venue_id,
        status=OrderStatus.pending,
        subtotal_cents=subtotal,
        discount_cents=0,
        total_cents=subtotal,
        contact_phone=body.contact_phone,
    )
    db.add(order)
    await db.flush()

    items = []
    for res in reservations:
        # Link reservation to order and mark pending_payment
        res.order_id = order.id
        res.status = ReservationStatus.pending_payment

        item = OrderItem(
            order_id=order.id,
            item_type="reservation",
            item_id=res.id,
            description=f"{res.slot_start_at.strftime('%m-%d')} {res.slot_start_at.strftime('%H:%M')}–{res.slot_end_at.strftime('%H:%M')}",
            quantity=1,
            unit_price_cents=res.amount_cents,
            total_cents=res.amount_cents,
        )
        db.add(item)
        items.append(item)

    await db.commit()
    await db.refresh(order)

    return OrderOut(
        id=str(order.id),
        status=order.status,
        subtotal_cents=order.subtotal_cents,
        discount_cents=order.discount_cents,
        total_cents=order.total_cents,
        contact_phone=order.contact_phone,
        items=[
            OrderItemOut(
                item_type=i.item_type,
                description=i.description,
                quantity=i.quantity,
                unit_price_cents=i.unit_price_cents,
                total_cents=i.total_cents,
            )
            for i in items
        ],
        created_at=order.created_at.isoformat(),
    )


@router.get("", response_model=list[OrderOut])
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    return [_order_to_out(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).where(
            Order.id == uuid.UUID(order_id), Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _order_to_out(order)


@router.post("/{order_id}/cancel", status_code=204)
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).where(
            Order.id == uuid.UUID(order_id), Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in (OrderStatus.pending,):
        raise HTTPException(status_code=400, detail="Order cannot be cancelled")

    from app.main import app

    redis = app.state.redis
    from app.services.booking import cancel_reservation

    for res in order.reservations:
        if res.status in (
            ReservationStatus.pending_payment,
            ReservationStatus.confirmed,
        ):
            await cancel_reservation(db, redis, res.id, current_user.id)

    order.status = OrderStatus.cancelled
    await db.commit()


def _order_to_out(order: Order) -> OrderOut:
    return OrderOut(
        id=str(order.id),
        status=order.status,
        subtotal_cents=order.subtotal_cents,
        discount_cents=order.discount_cents,
        total_cents=order.total_cents,
        contact_phone=order.contact_phone,
        items=[
            OrderItemOut(
                item_type=i.item_type,
                description=i.description,
                quantity=i.quantity,
                unit_price_cents=i.unit_price_cents,
                total_cents=i.total_cents,
            )
            for i in order.items
        ],
        created_at=order.created_at.isoformat(),
    )
