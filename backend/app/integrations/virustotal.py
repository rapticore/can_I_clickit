import httpx
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()

VT_URL_REPORT = "https://www.virustotal.com/api/v3/urls"


class VirusTotalClient:
    """VirusTotal API client for URL reputation checks."""

    async def scan_url(self, url: str) -> dict | None:
        settings = get_settings()
        if not settings.virustotal_api_key:
            logger.debug("virustotal_skipped", reason="no API key configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                import base64
                url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")

                resp = await client.get(
                    f"{VT_URL_REPORT}/{url_id}",
                    headers={"x-apikey": settings.virustotal_api_key},
                )

                if resp.status_code == 200:
                    data = resp.json()
                    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                    return {
                        "positives": stats.get("malicious", 0) + stats.get("suspicious", 0),
                        "total": sum(stats.values()),
                        "raw_stats": stats,
                    }

                if resp.status_code == 404:
                    return {"positives": 0, "total": 0}

                logger.warning("virustotal_error", status=resp.status_code)
                return None

        except Exception as exc:
            logger.error("virustotal_request_failed", error=str(exc))
            return None
