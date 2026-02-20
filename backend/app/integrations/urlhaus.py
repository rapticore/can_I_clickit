import httpx
import structlog

logger = structlog.get_logger()

URLHAUS_API_URL = "https://urlhaus-api.abuse.ch/v1/url/"


class URLHausClient:
    """URLhaus API client for malware URL checking."""

    async def check_url(self, url: str) -> dict | None:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    URLHAUS_API_URL,
                    data={"url": url},
                )

                if resp.status_code == 200:
                    result = resp.json()
                    return {
                        "threat_type": result.get("threat", ""),
                        "status": result.get("url_status", ""),
                        "is_malware": result.get("query_status") == "listed",
                        "tags": result.get("tags", []),
                    }

                return None

        except Exception as exc:
            logger.error("urlhaus_request_failed", error=str(exc))
            return None
