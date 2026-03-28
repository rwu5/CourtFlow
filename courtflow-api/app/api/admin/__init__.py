from fastapi import APIRouter
from app.api.admin.endpoints import organizations, venues, courts, pricing, memberships, reservations, court_blocks

router = APIRouter(prefix="/api/v1/admin")
router.include_router(organizations.router)
router.include_router(venues.router)
router.include_router(courts.router)
router.include_router(pricing.router)
router.include_router(memberships.router)
router.include_router(reservations.router)
router.include_router(court_blocks.router)
