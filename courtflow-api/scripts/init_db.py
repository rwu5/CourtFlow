"""Create all database tables and run dev seed.

Usage:  python -m scripts.init_db
"""

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.database import Base

# Import all models so they register with Base.metadata
import app.models  # noqa: F401


async def main():
    engine = create_async_engine(settings.database_url, echo=True)

    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

    await engine.dispose()

    # Run seed
    print("Running dev seed...")
    from seeds.seed_dev import seed
    await seed()


if __name__ == "__main__":
    asyncio.run(main())
