from datetime import date

from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.cache.redis_client import get_redis
from app.core.config import Settings, get_settings


async def check_rate_limit(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    """Enforce daily scan limit for free-tier users.

    Premium users (identified via request state) bypass the limit.
    """
    user_tier = getattr(request.state, "user_tier", "free")
    if user_tier == "premium":
        return

    user_id = getattr(request.state, "user_id", request.client.host if request.client else "unknown")
    redis = await get_redis()
    key = f"rate:{user_id}:{date.today().isoformat()}"

    current = await redis.get(key)
    if current is not None and int(current) >= settings.free_tier_daily_scans:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Free tier limit of {settings.free_tier_daily_scans} scans per day reached. Upgrade to premium for unlimited scans.",
        )

    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)
    await pipe.execute()
