import re

import structlog

from app.models.scan import ScanType, SignalResult, SignalSource

logger = structlog.get_logger()

URGENCY_PATTERNS = [
    (r"\b(urgent|immediately|right now|asap|within \d+ hours?)\b", 30),
    (r"\b(account.{0,20}(suspend|terminat|clos|lock|restrict))", 35),
    (r"\b(verify|confirm|update).{0,20}(account|identity|information)\b", 25),
    (r"\b(limited.time|act.now|expires?.today|last.chance|final.warning)\b", 30),
]

IMPERSONATION_PATTERNS = [
    (r"\b(your bank|bank of america|wells fargo|chase|citibank)\b", 25),
    (r"\b(irs|social security|medicare|department of)\b", 30),
    (r"\b(usps|fedex|ups|dhl|amazon).{0,30}(deliver|package|shipment)\b", 25),
    (r"\b(apple|microsoft|google|paypal).{0,20}(support|security|account)\b", 25),
    (r"\b(hey\s+(mom|dad|son|daughter|grandma|grandpa))", 30),
]

FINANCIAL_REQUEST_PATTERNS = [
    (r"\b(send|transfer|wire|pay).{0,30}(money|funds|gift.card|bitcoin|crypto)\b", 40),
    (r"\b(gift.card|itunes|google.play|steam).{0,20}(code|number|pin)\b", 45),
    (r"\b(western union|moneygram|zelle|venmo|cashapp)\b", 20),
    (r"\b(bitcoin|btc|ethereum|crypto).{0,20}(address|wallet|send)\b", 35),
]

SEXTORTION_PATTERNS = [
    (r"\b(compromising|intimate|explicit).{0,20}(photo|video|footage|material)\b", 40),
    (r"\b(browsing.history|webcam|camera).{0,20}(record|capture|access)\b", 40),
    (r"\b(pay|send).{0,30}(bitcoin|btc|crypto).{0,30}(wallet|address)\b", 35),
    (r"\b(release|share|publish|send.to).{0,20}(contacts|friends|family|everyone)\b", 35),
]

PIG_BUTCHERING_PATTERNS = [
    (r"\b(invest|trading|forex|crypto).{0,30}(platform|opportunity|profit|return)\b", 30),
    (r"\b(guaranteed|sure.thing|risk.free|100%.{0,5}(profit|return))\b", 35),
    (r"\b(special|exclusive|limited).{0,20}(investment|opportunity|platform)\b", 25),
    (r"\b(unlock|withdraw).{0,20}(funds|money|profit).{0,20}(fee|deposit|tax)\b", 45),
]

RANSOMWARE_PATTERNS = [
    (r"\b(files?.{0,10}(encrypt|lock)|encrypt.{0,10}files?)\b", 40),
    (r"\b(decryption|decrypt).{0,20}(key|tool|software)\b", 35),
    (r"\b(ransom|bitcoin|btc).{0,30}(pay|send|transfer)\b", 35),
    (r"\b(your.data|your.files).{0,20}(will.be|have.been).{0,10}(delet|destroy|publish)\b", 40),
]

KNOWN_SAFE_DOMAINS = {
    "google.com", "youtube.com", "facebook.com", "amazon.com",
    "apple.com", "microsoft.com", "github.com", "wikipedia.org",
    "linkedin.com", "twitter.com", "instagram.com", "reddit.com",
    "netflix.com", "spotify.com", "paypal.com", "chase.com",
    "bankofamerica.com", "wellsfargo.com", "usps.com", "ups.com",
    "fedex.com", "irs.gov", "ssa.gov",
}


class FastPathAnalyzer:
    """Fast path analysis: heuristics, regex patterns, blocklist lookups.

    Resolves 60-70% of scans in < 500ms.
    """

    async def analyze(
        self,
        content: str,
        urls: list[str],
        scan_type: ScanType,
    ) -> tuple[list[SignalResult], float]:
        signals: list[SignalResult] = []
        content_lower = content.lower()

        for pattern_set, source_name, pattern_label in [
            (URGENCY_PATTERNS, "urgency", "urgency_language"),
            (IMPERSONATION_PATTERNS, "impersonation", "impersonation_pattern"),
            (FINANCIAL_REQUEST_PATTERNS, "financial_request", "financial_request"),
            (SEXTORTION_PATTERNS, "sextortion", "sextortion_pattern"),
            (PIG_BUTCHERING_PATTERNS, "pig_butchering", "pig_butchering_pattern"),
            (RANSOMWARE_PATTERNS, "ransomware", "ransomware_pattern"),
        ]:
            score = self._check_patterns(content_lower, pattern_set)
            if score > 0:
                signals.append(SignalResult(
                    source=SignalSource.HEURISTIC,
                    score=min(score, 95),
                    detail=f"{pattern_label} detected (score: {score})",
                ))

        for url in urls:
            url_signals = await self._analyze_url_fast(url)
            signals.extend(url_signals)

        total_score = self._compute_confidence(signals)
        return signals, total_score

    @staticmethod
    def _check_patterns(text: str, patterns: list[tuple[str, int]]) -> float:
        total = 0.0
        for pattern, weight in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                total += weight
        return min(total, 95.0)

    async def _analyze_url_fast(self, url: str) -> list[SignalResult]:
        from urllib.parse import urlparse

        signals = []

        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
        except Exception:
            signals.append(SignalResult(
                source=SignalSource.HEURISTIC,
                score=60,
                detail="Malformed URL",
            ))
            return signals

        root_domain = ".".join(domain.split(".")[-2:]) if "." in domain else domain

        if root_domain in KNOWN_SAFE_DOMAINS:
            signals.append(SignalResult(
                source=SignalSource.BLOCKLIST,
                score=5,
                detail=f"Known safe domain: {root_domain}",
            ))
            return signals

        typosquat_score = self._check_typosquatting(root_domain)
        if typosquat_score > 0:
            signals.append(SignalResult(
                source=SignalSource.TYPOSQUATTING,
                score=typosquat_score,
                detail=f"Possible typosquatting: {root_domain}",
            ))

        if parsed.scheme == "http":
            signals.append(SignalResult(
                source=SignalSource.SSL_CHECK,
                score=30,
                detail="Non-HTTPS URL",
            ))

        suspicious_tlds = {".xyz", ".top", ".click", ".buzz", ".tk", ".ml", ".ga", ".cf", ".gq"}
        for tld in suspicious_tlds:
            if domain.endswith(tld):
                signals.append(SignalResult(
                    source=SignalSource.HEURISTIC,
                    score=35,
                    detail=f"Suspicious TLD: {tld}",
                ))
                break

        if len(url) > 200:
            signals.append(SignalResult(
                source=SignalSource.HEURISTIC,
                score=20,
                detail="Unusually long URL",
            ))

        if url.count("/") > 8 or url.count("@") > 0:
            signals.append(SignalResult(
                source=SignalSource.HEURISTIC,
                score=30,
                detail="Suspicious URL structure",
            ))

        return signals

    @staticmethod
    def _check_typosquatting(domain: str) -> float:
        top_domains = [
            "google.com", "facebook.com", "amazon.com", "apple.com",
            "microsoft.com", "paypal.com", "netflix.com", "chase.com",
            "bankofamerica.com", "wellsfargo.com", "instagram.com",
        ]
        for top in top_domains:
            distance = _levenshtein(domain, top)
            if 0 < distance <= 2:
                return 70.0 + (2 - distance) * 10
        return 0.0

    @staticmethod
    def _compute_confidence(signals: list[SignalResult]) -> float:
        if not signals:
            return 30.0
        max_score = max(s.score for s in signals)
        avg_score = sum(s.score for s in signals) / len(signals)
        return min(max_score * 0.7 + avg_score * 0.3, 100.0)


def _levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]
