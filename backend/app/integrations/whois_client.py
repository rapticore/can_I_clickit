from datetime import datetime, timezone

import structlog

logger = structlog.get_logger()


class WhoisClient:
    """WHOIS lookup for domain age and registration details."""

    async def lookup(self, domain: str) -> dict | None:
        try:
            import whois

            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            expiration_date = w.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]

            age_days = None
            if creation_date:
                if creation_date.tzinfo is None:
                    creation_date = creation_date.replace(tzinfo=timezone.utc)
                age_days = (datetime.now(timezone.utc) - creation_date).days

            return {
                "domain": domain,
                "registrar": w.registrar,
                "creation_date": creation_date.isoformat() if creation_date else None,
                "expiration_date": expiration_date.isoformat() if expiration_date else None,
                "age_days": age_days,
                "name_servers": w.name_servers if hasattr(w, "name_servers") else [],
            }

        except Exception as exc:
            logger.debug("whois_lookup_failed", domain=domain, error=str(exc))
            return None
