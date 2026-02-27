import logging

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

from app.core.config import Settings, get_settings

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
