from collections.abc import Generator

import redis

from .config import settings

connection_pool = redis.ConnectionPool.from_url(str(settings.CELERY_BACKEND_URL))


def get_redis_session() -> Generator[redis.Redis, None, None]:
    r = redis.Redis(connection_pool=connection_pool)

    try:
        yield r
    finally:
        r.close()
