import logging
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from app.configs.settings import settings

logger = logging.getLogger(__name__)

# -----------------------------
# Database URL
# -----------------------------
DATABASE_URL = settings.DB_URL  # example: mysql+asyncmy://user:pass@localhost/db

if not DATABASE_URL:
    raise ValueError("Database URL not configured. Please set DB_URL.")

# -----------------------------
# Async Engine (Non-blocking)
# -----------------------------
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # base connections
    max_overflow=10,        # extra burst connections
    pool_timeout=30,        # wait time before error
    pool_recycle=1800,      # avoid MySQL timeout (IMPORTANT)
    pool_pre_ping=True,     # auto reconnect dead connections
    echo=False,             # log SQL queries
    future=True,            # use async/await syntax
)

Base = declarative_base()

# -----------------------------
# Async Session Factory
# -----------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# -----------------------------
# Dependency (FastAPI)
# -----------------------------
@asynccontextmanager
async def get_async_db():
    """
    Async DB session (non-blocking)
    Usage:
        async with get_async_db() as db:
            ...
    """
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"DB session rollback due to error: {e}")
        raise
    finally:
        await session.close()


# -----------------------------
# Health Check
# -----------------------------
async def check_database_connection() -> bool:
    """
    Verify DB connection
    """
    try:
        async with get_async_db() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✅ Database connection OK")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


# -----------------------------
# Graceful Shutdown Cleanup
# -----------------------------
async def cleanup_connections():
    """
    Close all DB connections (call on app shutdown)
    """
    try:
        await async_engine.dispose()
        logger.info("🧹 Database connections closed")
    except Exception as e:
        logger.error(f"Error closing DB connections: {e}")