import re

import structlog

from app.models.scan import SignalResult, SignalSource

logger = structlog.get_logger()


class IntentDetector:
    """Analyzes the communicative intent of a message.

    Most tools analyze artifacts (URLs, files). This engine analyzes intent:
    is the message trying to create urgency, impersonate someone trusted,
    or manipulate the recipient into an unusual action?

    This is the core differentiator -- catches social engineering that
    has no malicious artifact at all.
    """

    def detect(self, content: str) -> list[SignalResult]:
        signals = []
        content_lower = content.lower()

        intent_scores = {
            "urgency_creation": self._score_urgency_creation(content_lower),
            "authority_exploitation": self._score_authority_exploitation(content_lower),
            "emotional_manipulation": self._score_emotional_manipulation(content_lower),
            "unusual_action_request": self._score_unusual_action(content_lower),
            "information_harvesting": self._score_info_harvesting(content_lower),
            "relationship_exploitation": self._score_relationship_exploitation(content_lower),
        }

        for intent_type, score in intent_scores.items():
            if score > 20:
                signals.append(SignalResult(
                    source=SignalSource.INTENT_DETECTION,
                    score=score,
                    detail=f"Intent: {intent_type.replace('_', ' ')} (score: {score:.0f})",
                ))

        active_intents = sum(1 for s in intent_scores.values() if s > 20)
        if active_intents >= 3:
            signals.append(SignalResult(
                source=SignalSource.INTENT_DETECTION,
                score=min(85, sum(intent_scores.values()) / len(intent_scores) * 1.5),
                detail=f"Multiple social engineering intents detected ({active_intents} types)",
            ))

        return signals

    @staticmethod
    def _score_urgency_creation(text: str) -> float:
        patterns = [
            (r"\b(within|in)\s+\d+\s+(hour|minute|day)s?\b", 25),
            (r"\b(expire|expiring|expires)\s+(today|soon|tomorrow)\b", 25),
            (r"\b(immediate|urgent|emergency|critical)\s+(action|attention|response)\b", 30),
            (r"\bfinal\s+(notice|warning|chance)\b", 30),
            (r"\b(act|respond|reply)\s+(now|immediately|quickly)\b", 25),
        ]
        return _sum_pattern_scores(text, patterns)

    @staticmethod
    def _score_authority_exploitation(text: str) -> float:
        patterns = [
            (r"\b(official|authorized|certified)\s+(notice|communication|representative)\b", 25),
            (r"\b(department|bureau|agency|office)\s+of\b", 20),
            (r"\b(compliance|regulatory|enforcement)\s+(team|division|action|department)\b", 25),
            (r"\bthis is a (legal|official|mandatory)\b", 30),
        ]
        return _sum_pattern_scores(text, patterns)

    @staticmethod
    def _score_emotional_manipulation(text: str) -> float:
        patterns = [
            (r"\b(help|please|desperate|scared|worried)\b.*\b(money|send|transfer)\b", 30),
            (r"\b(love|trust|care)\b.*\b(invest|opportunity|special)\b", 25),
            (r"\b(embarrass|shame|expose|reveal)\b", 25),
            (r"\b(congratulations|selected|chosen|winner)\b", 20),
        ]
        return _sum_pattern_scores(text, patterns)

    @staticmethod
    def _score_unusual_action(text: str) -> float:
        patterns = [
            (r"\b(gift\s*card|itunes|google\s*play|steam)\b.*\b(buy|purchase|send)\b|\b(buy|purchase|send)\b.*\b(gift\s*card|itunes|google\s*play|steam)\b", 40),
            (r"\b(wire|transfer|western\s*union|moneygram)\b", 25),
            (r"\b(download|install)\s+(this|the)\s+(app|software|tool)\b", 30),
            (r"\b(remote\s*access|teamviewer|anydesk|logmein)\b", 35),
            (r"\b(bitcoin|btc|crypto)\b.*\b(address|wallet|send)\b|\b(address|wallet|send)\b.*\b(bitcoin|btc|crypto)\b", 35),
        ]
        return _sum_pattern_scores(text, patterns)

    @staticmethod
    def _score_info_harvesting(text: str) -> float:
        patterns = [
            (r"\b(verify|confirm|update)\s+(your|the)\s+(ssn|social\s*security|tax\s*id)\b", 40),
            (r"\b(enter|provide|send)\s+(your|the)\s+(password|pin|code)\b", 35),
            (r"\b(date\s*of\s*birth|dob|mother'?s?\s*maiden)\b", 30),
            (r"\b(credit\s*card|bank\s*account|routing)\s*(number|info|details)\b", 35),
        ]
        return _sum_pattern_scores(text, patterns)

    @staticmethod
    def _score_relationship_exploitation(text: str) -> float:
        patterns = [
            (r"\b(hey\s+(mom|dad|son|daughter|grandma|grandpa))\b", 30),
            (r"\b(lost|new|broken)\s+(my\s+)?(phone|number)\b.*\b(this|new)\s+(is|number)\b", 35),
            (r"\b(don'?t\s+tell|keep\s+this\s+between|secret)\b", 25),
            (r"\b(i'?m\s+in\s+trouble|need\s+help|emergency)\b.*\b(money|send|transfer)\b", 35),
        ]
        return _sum_pattern_scores(text, patterns)


def _sum_pattern_scores(text: str, patterns: list[tuple[str, int]]) -> float:
    total = 0.0
    for pattern, weight in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            total += weight
    return min(total, 90.0)
