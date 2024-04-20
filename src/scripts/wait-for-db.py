import asyncio
import logging

from sqlalchemy import select
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_fixed,
)

from src.core.database import get_async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MAX_TRIES = 60 * 5  # 5 minutes
WAIT_SECONDS = 5


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECONDS),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def wait_for_db() -> None:
    """Wait for the database to be ready.

    Raises:
        Exception: If the database is not ready after the maximum number of tries.

    Returns:
        None: The database is ready.
    """
    try:
        async for session in get_async_session():
            await session.execute(select(1))
    except Exception as e:
        logger.error(e)
        raise e


async def main() -> None:
    """Run the main script."""
    logger.info("Waiting for database...")
    await wait_for_db()
    logger.info("Database is ready!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
