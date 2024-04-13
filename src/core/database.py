from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI_ASYNC
)

SessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async session from the database.

    Yields:
        AsyncGenerator[AsyncSession, None]: The async session.

    Examples:
        >>> async with get_async_session() as session:
        ...     await session.execute(select(User)).scalars().all()

    Returns:
        AsyncGenerator[AsyncSession, None]: The async session.
    """
    async with SessionLocal() as session:
        yield session
