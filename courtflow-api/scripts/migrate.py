"""Create any new database tables without re-seeding.

This runs Base.metadata.create_all which only creates tables that
don't already exist — it will NOT drop or alter existing tables.

Usage:  python -m scripts.migrate
"""

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.database import Base

# Import all models so they register with Base.metadata
import app.models  # noqa: F401


async def main():
    engine = create_async_engine(settings.database_url, echo=True)

    print("Creating new tables (existing tables are untouched)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Done.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
