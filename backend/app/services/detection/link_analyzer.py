import ssl
import socket
from urllib.parse import urlparse

import httpx
import structlog

from app.models.scan import SignalResult, SignalSource

logger = structlog.get_logger()

MAX_REDIRECTS = 10


class LinkAnalyzer:
    """Full link analysis: domain reputation, redirects, typosquatting, SSL, WHOIS."""

    async def analyze(self, url: str) -> list[SignalResult]:
        signals: list[SignalResult] = []

        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
        except Exception:
            return [SignalResult(source=SignalSource.HEURISTIC, score=60, detail="Malformed URL")]

        redirect_signals = await self._check_redirects(url)
        signals.extend(redirect_signals)

        ssl_signals = await self._check_ssl(domain)
        signals.extend(ssl_signals)

        domain_age_signals = await self._check_domain_age(domain)
        signals.extend(domain_age_signals)

        reputation_signals = await self._check_reputation(url)
        signals.extend(reputation_signals)

        return signals

    async def _check_redirects(self, url: str) -> list[SignalResult]:
        signals = []
        try:
            async with httpx.AsyncClient(follow_redirects=False, timeout=5.0) as client:
                redirect_count = 0
                current_url = url
                seen_domains = set()

                while redirect_count < MAX_REDIRECTS:
                    resp = await client.head(current_url)
                    parsed = urlparse(current_url)
                    seen_domains.add(parsed.hostname)

                    if resp.status_code not in (301, 302, 303, 307, 308):
                        break

                    current_url = resp.headers.get("location", "")
                    if not current_url:
                        break
                    redirect_count += 1

                if redirect_count >= 3:
                    signals.append(SignalResult(
                        source=SignalSource.REDIRECT_ANALYSIS,
                        score=min(30 + redirect_count * 10, 80),
                        detail=f"URL has {redirect_count} redirects across {len(seen_domains)} domains",
                    ))

                if len(seen_domains) >= 3:
                    signals.append(SignalResult(
                        source=SignalSource.REDIRECT_ANALYSIS,
                        score=60,
                        detail=f"Redirect chain crosses {len(seen_domains)} different domains",
                    ))

        except httpx.TimeoutException:
            signals.append(SignalResult(
                source=SignalSource.HEURISTIC,
                score=25,
                detail="URL timed out during redirect check",
            ))
        except Exception as exc:
            logger.warning("redirect_check_failed", url=url, error=str(exc))

        return signals

    async def _check_ssl(self, domain: str) -> list[SignalResult]:
        signals = []
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=3) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        subject = dict(x[0] for x in cert.get("subject", ()))
                        cert_cn = subject.get("commonName", "")
                        if cert_cn and domain not in cert_cn and "*" not in cert_cn:
                            signals.append(SignalResult(
                                source=SignalSource.SSL_CHECK,
                                score=50,
                                detail=f"SSL certificate CN ({cert_cn}) does not match domain ({domain})",
                            ))
        except ssl.SSLCertVerificationError:
            signals.append(SignalResult(
                source=SignalSource.SSL_CHECK,
                score=60,
                detail="SSL certificate verification failed",
            ))
        except Exception:
            pass

        return signals

    async def _check_domain_age(self, domain: str) -> list[SignalResult]:
        """Check domain age via WHOIS. New domains are higher risk."""
        signals = []
        try:
            from app.integrations.whois_client import WhoisClient

            whois_client = WhoisClient()
            result = await whois_client.lookup(domain)
            age_days = result.get("age_days") if result else None
            if age_days is not None:
                if age_days < 30:
                    signals.append(SignalResult(
                        source=SignalSource.DOMAIN_AGE,
                        score=75,
                        detail=f"Domain registered {age_days} days ago (very new)",
                    ))
                elif age_days < 90:
                    signals.append(SignalResult(
                        source=SignalSource.DOMAIN_AGE,
                        score=50,
                        detail=f"Domain registered {age_days} days ago (new)",
                    ))
                elif age_days < 365:
                    signals.append(SignalResult(
                        source=SignalSource.DOMAIN_AGE,
                        score=25,
                        detail=f"Domain registered {age_days} days ago (less than 1 year)",
                    ))
        except Exception as exc:
            logger.debug("whois_lookup_failed", domain=domain, error=str(exc))

        return signals

    async def _check_reputation(self, url: str) -> list[SignalResult]:
        """Check URL against threat intelligence feeds."""
        from app.integrations.phishtank import PhishTankClient
        from app.integrations.urlhaus import URLHausClient
        from app.integrations.virustotal import VirusTotalClient

        signals = []
        try:
            vt = VirusTotalClient()
            vt_result = await vt.scan_url(url)
            if vt_result and vt_result.get("positives", 0) > 0:
                positives = vt_result["positives"]
                total = vt_result.get("total", 1)
                score = min((positives / max(total, 1)) * 100, 95)
                signals.append(SignalResult(
                    source=SignalSource.BLOCKLIST,
                    score=score,
                    detail=f"Flagged by {positives}/{total} threat intelligence sources",
                ))

            phishtank = PhishTankClient()
            pt_result = await phishtank.check_url(url)
            if pt_result and pt_result.get("is_phish"):
                signals.append(SignalResult(
                    source=SignalSource.BLOCKLIST,
                    score=85.0,
                    detail="PhishTank reports this URL as phishing",
                ))

            urlhaus = URLHausClient()
            uh_result = await urlhaus.check_url(url)
            if uh_result and uh_result.get("is_malware"):
                threat_type = uh_result.get("threat_type") or "malware"
                signals.append(SignalResult(
                    source=SignalSource.BLOCKLIST,
                    score=90.0,
                    detail=f"URLhaus flagged URL as {threat_type}",
                ))
        except Exception as exc:
            logger.debug("reputation_check_failed", url=url, error=str(exc))

        return signals
