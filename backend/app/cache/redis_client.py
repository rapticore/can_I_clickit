import hashlib

import redis.asyncio as redis

from app.core.config import get_settings

_redis_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis_pool
    if _redis_pool is None:
        settings = get_settings()
        _redis_pool = redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _redis_pool


async def close_redis() -> None:
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None


def hash_input(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


async def get_cached_verdict(content_hash: str) -> dict | None:
    r = await get_redis()
    import json

    cached = await r.get(f"verdict:{content_hash}")
    if cached:
        return json.loads(cached)
    return None


async def set_cached_verdict(content_hash: str, verdict: dict, ttl: int | None = None) -> None:
    import json

    r = await get_redis()
    settings = get_settings()
    ttl = ttl or settings.cache_ttl_seconds
    await r.setex(f"verdict:{content_hash}", ttl, json.dumps(verdict))
