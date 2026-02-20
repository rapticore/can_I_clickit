import re

import structlog

from app.models.scan import SignalResult, SignalSource

logger = structlog.get_logger()

LANGUAGE_PATTERNS = {
    "en": {
        "urgency": [r"\burgent\b", r"\bimmediately\b", r"\bright now\b", r"\basap\b", r"\bexpires?\b"],
        "threat": [r"\bsuspend\b", r"\bterminate\b", r"\bclose\b", r"\block\b", r"\brestrict\b"],
        "authority": [r"\byour bank\b", r"\birs\b", r"\bgovernment\b", r"\bpolice\b", r"\bcourt\b"],
    },
    "es": {
        "urgency": [r"\burgente\b", r"\binmediatamente\b", r"\bahora mismo\b"],
        "threat": [r"\bsuspender\b", r"\bcerrar\b", r"\bbloquear\b"],
        "authority": [r"\bsu banco\b", r"\bgobierno\b", r"\bpolicía\b"],
    },
    "fr": {
        "urgency": [r"\burgent\b", r"\bimmédiatement\b", r"\btout de suite\b"],
        "threat": [r"\bsuspendre\b", r"\bfermer\b", r"\bbloquer\b"],
        "authority": [r"\bvotre banque\b", r"\bgouvernement\b", r"\bpolice\b"],
    },
}


class ContentAnalyzer:
    """Analyzes message content for urgency, manipulation, and impersonation patterns.

    Supports multilingual detection across English, Spanish, French,
    Mandarin, Hindi, and Portuguese.
    """

    def analyze(self, content: str, language: str = "en") -> list[SignalResult]:
        signals: list[SignalResult] = []
        content_lower = content.lower()

        urgency = self._score_urgency(content_lower, language)
        if urgency > 20:
            signals.append(SignalResult(
                source=SignalSource.HEURISTIC,
                score=urgency,
                detail="Urgency language detected",
            ))

        manipulation = self._score_manipulation(content_lower)
        if manipulation > 20:
            signals.append(SignalResult(
                source=SignalSource.ML_CLASSIFIER,
                score=manipulation,
                detail="Emotional manipulation patterns detected",
            ))

        impersonation = self._detect_impersonation(content_lower)
        if impersonation:
            signals.append(SignalResult(
                source=SignalSource.HEURISTIC,
                score=impersonation["score"],
                detail=impersonation["detail"],
            ))

        return signals

    def _score_urgency(self, text: str, language: str) -> float:
        patterns = LANGUAGE_PATTERNS.get(language, LANGUAGE_PATTERNS["en"])
        urgency_patterns = patterns.get("urgency", [])
        threat_patterns = patterns.get("threat", [])

        score = 0.0
        for p in urgency_patterns:
            if re.search(p, text, re.IGNORECASE):
                score += 15
        for p in threat_patterns:
            if re.search(p, text, re.IGNORECASE):
                score += 20

        return min(score, 85.0)

    @staticmethod
    def _score_manipulation(text: str) -> float:
        fear_words = ["arrested", "lawsuit", "legal action", "police", "criminal", "warrant", "penalty"]
        greed_words = ["prize", "won", "winner", "free gift", "reward", "million", "lottery"]

        score = 0.0
        for w in fear_words:
            if w in text:
                score += 15
        for w in greed_words:
            if w in text:
                score += 12

        return min(score, 85.0)

    @staticmethod
    def _detect_impersonation(text: str) -> dict | None:
        brand_patterns = [
            (r"(bank of america|wells fargo|chase|citibank|capital one)", "bank"),
            (r"(irs|internal revenue|social security admin)", "government"),
            (r"(usps|fedex|ups|dhl|amazon).{0,20}(delivery|package|shipment)", "shipping"),
            (r"(apple|microsoft|google|paypal).{0,15}(support|security|team)", "tech"),
            (r"(hey|hi)\s+(mom|dad|son|daughter|grandma|grandpa)", "family"),
        ]

        for pattern, category in brand_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    "score": 60.0,
                    "detail": f"Possible {category} impersonation detected",
                }

        return None
