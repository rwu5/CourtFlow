from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, venues, bookings, orders, memberships

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(venues.router)
router.include_router(bookings.router)
router.include_router(orders.router)
router.include_router(memberships.router)
