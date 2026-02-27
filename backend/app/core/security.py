import logging

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

from app.core.config import Settings, get_settings
from app.db.database import get_db
from app.db.models import User
from app.services.auth import decode_access_token

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    if not settings.api_keys:
        if settings.debug:
            logger.warning("Auth bypassed: no API keys configured (debug mode)")
            return "dev-mode"
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: no API keys configured",
        )
    if api_key is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    if api_key not in settings.api_keys:
        logger.warning("Invalid API key attempt: %s", api_key[:8] + "...")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key


async def get_current_user(
    request: Request,
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> User:
    # 1. Try JWT from cookie
    token = request.cookies.get("clickit_session")
    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            result = await db.execute(select(User).where(User.id == payload["sub"]))
            user = result.scalar_one_or_none()
            if user:
                return user

    # 2. Fall back to X-API-Key header
    if api_key:
        # Check global keys list first
        if api_key in settings.api_keys:
            # Global key — find or create implicit user
            import hashlib
            digest = hashlib.sha256(api_key.encode()).hexdigest()[:20]
            email = f"user-{digest}@local.clickit"
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                user = User(email=email, hashed_password="not-used", tier="free")
                db.add(user)
                await db.commit()
                await db.refresh(user)
            return user

        # Check per-user api_key column
        result = await db.execute(select(User).where(User.api_key == api_key))
        user = result.scalar_one_or_none()
        if user:
            return user

    # 3. Debug bypass
    if settings.debug and not token and not api_key:
        logger.warning("Auth bypassed: debug mode, no credentials provided")
        email = "debug-user@local.clickit"
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            user = User(email=email, hashed_password="not-used", tier="free")
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    # 4. Unauthorized
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide a session cookie or API key.",
    )
