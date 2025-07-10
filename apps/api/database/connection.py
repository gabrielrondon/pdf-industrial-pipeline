from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager, asynccontextmanager
from typing import AsyncGenerator, Generator
import logging

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# Synchronous engine and session
engine = create_engine(
    settings.database_url,
    poolclass=pool.QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.debug,  # Log SQL in debug mode
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


# Asynchronous engine and session
async_engine = create_async_engine(
    settings.database_url_async,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_pre_ping=True,
    echo=settings.debug,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Dependency for synchronous database sessions.
    Usage:
        with get_db() as db:
            result = db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for asynchronous database sessions.
    Usage:
        async with get_async_db() as db:
            result = await db.execute(select(Model))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db_dependency() -> Generator[Session, None, None]:
    """
    FastAPI dependency for synchronous endpoints.
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db_dependency)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for asynchronous endpoints.
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db_dependency)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def init_db():
    """Initialize database tables"""
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


async def init_async_db():
    """Initialize database tables asynchronously"""
    from database.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


def close_db():
    """Close database connections"""
    engine.dispose()
    logger.info("Database connections closed")


async def close_async_db():
    """Close async database connections"""
    await async_engine.dispose()
    logger.info("Async database connections closed")