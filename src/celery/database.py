from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_size=5, max_overflow=0)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get a session from the database.

    Yields:
        Generator[Session, None, None]: The session.

    Examples:
        >>> with get_session() as session:
        ...     session.query(User).all()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
