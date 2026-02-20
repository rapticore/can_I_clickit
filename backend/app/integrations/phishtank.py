import httpx
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()

PHISHTANK_API_URL = "https://checkurl.phishtank.com/checkurl/"


class PhishTankClient:
    """PhishTank API client for phishing URL verification."""

    async def check_url(self, url: str) -> dict | None:
        settings = get_settings()

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                data = {
                    "url": url,
                    "format": "json",
                }
                if settings.phishtank_api_key:
                    data["app_key"] = settings.phishtank_api_key

                resp = await client.post(PHISHTANK_API_URL, data=data)

                if resp.status_code == 200:
                    result = resp.json()
                    results = result.get("results", {})
                    return {
                        "in_database": results.get("in_database", False),
                        "is_phish": results.get("verified", False),
                        "verified": results.get("verified", False),
                    }

                return None

        except Exception as exc:
            logger.error("phishtank_request_failed", error=str(exc))
            return None
