import redis
from typing import Optional
from backend.app.core.config import settings

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Returns a singleton Redis client connected to the configured Redis Stack instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DB,
            socket_connect_timeout=1.5,
            socket_timeout=1.5,
            decode_responses=False,  # Keep binary for vector payloads
        )
    return _redis_client


def ping_redis() -> bool:
    """Tests if Redis Stack server is reachable."""
    try:
        client = get_redis_client()
        return client.ping()
    except Exception:
        return False
