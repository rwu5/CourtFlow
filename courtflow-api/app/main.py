from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.core.config import settings
from app.api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
    yield
    # Shutdown
    await app.state.redis.aclose()


app = FastAPI(
    title="CourtFlow API",
    version="0.1.0",
    description="Multi-tenant tennis venue commerce platform",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else [settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
