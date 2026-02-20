from fastapi import APIRouter, Depends

from app.cache.redis_client import get_redis
from app.core.config import Settings, get_settings
from app.db.database import check_db_connection

router = APIRouter()


@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    checks = {"api": "ok", "version": settings.app_version}

    db_ok = await check_db_connection()
    checks["db"] = "ok" if db_ok else "unavailable"

    try:
        r = await get_redis()
        await r.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "unavailable"

    status = "healthy" if all(v == "ok" for k, v in checks.items() if k != "version") else "degraded"

    return {"status": status, "checks": checks}
