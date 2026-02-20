import structlog

from app.models.scan import ScanType, SignalResult, SignalSource

logger = structlog.get_logger()

PHISHING_KEYWORDS_WEIGHTED = {
    "verify your account": 0.8,
    "confirm your identity": 0.75,
    "unusual activity": 0.7,
    "update your payment": 0.75,
    "click here to": 0.5,
    "dear customer": 0.4,
    "dear user": 0.45,
    "your account has been": 0.7,
    "suspended": 0.6,
    "locked": 0.55,
    "unauthorized": 0.6,
    "expire": 0.5,
    "within 24 hours": 0.7,
    "immediately": 0.5,
    "win": 0.35,
    "congratulations": 0.4,
    "lottery": 0.8,
    "inheritance": 0.8,
    "nigerian prince": 0.95,
    "wire transfer": 0.7,
    "social security number": 0.85,
    "ssn": 0.8,
    "password": 0.3,
    "login credentials": 0.6,
}

MANIPULATION_INDICATORS = {
    "fear": [
        "arrested", "lawsuit", "legal action", "police", "criminal",
        "warrant", "jail", "investigation", "penalty", "fine",
    ],
    "greed": [
        "prize", "won", "winner", "free", "gift", "reward",
        "million", "billion", "lottery", "jackpot", "cash",
    ],
    "urgency": [
        "now", "today", "immediately", "hurry", "quick",
        "fast", "deadline", "final", "last chance", "expir",
    ],
    "authority": [
        "government", "irs", "fbi", "cia", "police",
        "court", "judge", "officer", "agent", "official",
    ],
    "curiosity": [
        "you won't believe", "shocking", "secret", "exclusive",
        "revealed", "breaking", "incredible", "must see",
    ],
}


class MLPathAnalyzer:
    """ML-based analysis: phishing classification, intent detection, manipulation scoring.

    Runs when fast path confidence is < 80. Adds 1-2s latency.

    In production this would load a fine-tuned DistilBERT/BERT model.
    The current implementation uses a weighted keyword approach as a
    stand-in that can be swapped for the real model without API changes.
    """

    async def analyze(
        self,
        content: str,
        urls: list[str],
        scan_type: ScanType,
    ) -> tuple[list[SignalResult], float]:
        signals: list[SignalResult] = []
        content_lower = content.lower()

        phishing_score = self._classify_phishing(content_lower)
        if phishing_score > 30:
            signals.append(SignalResult(
                source=SignalSource.ML_CLASSIFIER,
                score=phishing_score,
                detail=f"Phishing classifier score: {phishing_score:.0f}",
            ))

        intent_score, intent_detail = self._detect_intent(content_lower)
        if intent_score > 25:
            signals.append(SignalResult(
                source=SignalSource.INTENT_DETECTION,
                score=intent_score,
                detail=intent_detail,
            ))

        manipulation_score, manipulation_types = self._score_manipulation(content_lower)
        if manipulation_score > 20:
            signals.append(SignalResult(
                source=SignalSource.ML_CLASSIFIER,
                score=manipulation_score,
                detail=f"Emotional manipulation detected: {', '.join(manipulation_types)}",
            ))

        total_score = self._compute_confidence(signals)
        return signals, total_score

    @staticmethod
    def _classify_phishing(text: str) -> float:
        score = 0.0
        matched = 0
        for keyword, weight in PHISHING_KEYWORDS_WEIGHTED.items():
            if keyword in text:
                score += weight * 100
                matched += 1
        if matched == 0:
            return 0.0
        return min(score / max(matched, 1), 95.0)

    @staticmethod
    def _detect_intent(text: str) -> tuple[float, str]:
        """Detect the communicative intent of the message.

        Looks for patterns indicating social engineering intent rather than
        just checking for malicious artifacts.
        """
        intent_signals = []
        score = 0.0

        has_urgency = any(w in text for w in ["immediately", "urgent", "now", "asap", "hurry"])
        has_action_request = any(w in text for w in ["click", "call", "send", "verify", "confirm", "update", "login"])
        has_consequence = any(w in text for w in ["suspend", "close", "lock", "terminate", "arrest", "fine", "penalty"])
        has_impersonation = any(w in text for w in ["your bank", "irs", "social security", "microsoft support", "apple support"])
        has_financial = any(w in text for w in ["send money", "gift card", "wire", "bitcoin", "payment"])

        if has_urgency:
            score += 20
            intent_signals.append("urgency pressure")
        if has_action_request:
            score += 15
            intent_signals.append("action request")
        if has_consequence:
            score += 25
            intent_signals.append("threat of consequences")
        if has_impersonation:
            score += 25
            intent_signals.append("authority impersonation")
        if has_financial:
            score += 30
            intent_signals.append("financial request")

        if len(intent_signals) >= 3:
            score *= 1.3

        detail = f"Intent analysis: {', '.join(intent_signals)}" if intent_signals else "No clear social engineering intent"
        return min(score, 95.0), detail

    @staticmethod
    def _score_manipulation(text: str) -> tuple[float, list[str]]:
        detected_types = []
        total_score = 0.0

        for manip_type, keywords in MANIPULATION_INDICATORS.items():
            count = sum(1 for kw in keywords if kw in text)
            if count >= 2:
                detected_types.append(manip_type)
                total_score += count * 10

        return min(total_score, 90.0), detected_types

    @staticmethod
    def _compute_confidence(signals: list[SignalResult]) -> float:
        if not signals:
            return 30.0
        max_score = max(s.score for s in signals)
        avg_score = sum(s.score for s in signals) / len(signals)
        return min(max_score * 0.6 + avg_score * 0.4, 100.0)
