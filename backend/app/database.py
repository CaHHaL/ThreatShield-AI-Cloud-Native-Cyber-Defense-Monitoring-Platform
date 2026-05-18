from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Create async engine — pool_pre_ping ensures stale connections are detected
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db():
    """FastAPI dependency: provides an async database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
