import structlog

from app.models.scan import ConfidenceLevel, SignalSource, ThreatLevel
from app.models.verdict import (
    CONSEQUENCE_TEMPLATES,
    SAFE_ACTION_TEMPLATES,
    VerdictInput,
    VerdictOutput,
)

logger = structlog.get_logger()

DANGEROUS_THRESHOLD = 70.0
SUSPICIOUS_THRESHOLD = 40.0

SAFE_VERDICT_DISCLAIMER = "This appears safe based on our analysis, but no system can guarantee 100% accuracy."


class VerdictEngine:
    """Compute final verdict from aggregated signals.

    Implements safety bias: low-confidence verdicts always default
    to suspicious, never safe. Single-signal safe verdicts are
    capped at medium confidence.
    """

    def compute(self, input: VerdictInput) -> VerdictOutput:
        threat_level = self._classify_threat(input.raw_score)
        confidence, confidence_score = self._calibrate_confidence(input)

        threat_level = self._apply_safety_bias(threat_level, confidence, input)

        scam_pattern = self._detect_scam_pattern(input)
        consequence = self._generate_consequence(threat_level, scam_pattern, input)
        safe_action = self._generate_safe_action(scam_pattern, input)
        explanation = self._generate_explanation(input, threat_level, confidence)
        summary = self._generate_summary(threat_level, confidence, scam_pattern)

        return VerdictOutput(
            threat_level=threat_level,
            confidence=confidence,
            confidence_score=confidence_score,
            verdict_summary=summary,
            consequence_warning=consequence,
            safe_action_suggestion=safe_action,
            explanation=explanation,
            scam_pattern=scam_pattern,
        )

    @staticmethod
    def _classify_threat(score: float) -> ThreatLevel:
        if score >= DANGEROUS_THRESHOLD:
            return ThreatLevel.DANGEROUS
        if score >= SUSPICIOUS_THRESHOLD:
            return ThreatLevel.SUSPICIOUS
        return ThreatLevel.SAFE

    @staticmethod
    def _calibrate_confidence(input: VerdictInput) -> tuple[ConfidenceLevel, float]:
        signals = input.signals
        if not signals:
            return ConfidenceLevel.LOW, 30.0

        source_types = {s.source for s in signals}
        high_score_count = sum(1 for s in signals if s.score >= 70)
        avg_score = sum(s.score for s in signals) / len(signals)

        if len(source_types) >= 3 and high_score_count >= 2:
            return ConfidenceLevel.HIGH, min(avg_score * 1.2, 95.0)

        if len(source_types) >= 2 or high_score_count >= 1:
            return ConfidenceLevel.MEDIUM, min(avg_score, 80.0)

        return ConfidenceLevel.LOW, min(avg_score * 0.8, 60.0)

    @staticmethod
    def _apply_safety_bias(
        threat_level: ThreatLevel,
        confidence: ConfidenceLevel,
        input: VerdictInput,
    ) -> ThreatLevel:
        """Emergency confidence override: low confidence never produces 'safe'."""
        if threat_level == ThreatLevel.SAFE and confidence == ConfidenceLevel.LOW:
            return ThreatLevel.SUSPICIOUS

        if threat_level == ThreatLevel.SAFE:
            source_types = {s.source for s in input.signals}
            if len(source_types) <= 1:
                return ThreatLevel.SAFE

        return threat_level

    @staticmethod
    def _detect_scam_pattern(input: VerdictInput) -> str | None:
        combined = " ".join(s.detail.lower() for s in input.signals)
        content = input.content_snippet.lower()
        all_text = combined + " " + content

        if "sextortion" in all_text or "blackmail" in all_text:
            return "sextortion"
        if "pig_butchering" in all_text or "romance" in all_text or "investment scam" in all_text:
            return "pig_butchering"
        if "ransomware" in all_text or "encrypt" in all_text:
            return "ransomware_bluff"
        if "impersonation" in all_text or "family" in all_text:
            return "impersonation"
        if "gift card" in all_text or "wire" in all_text:
            return "gift_card_scam"
        if "phishing" in all_text or "credential" in all_text:
            return "phishing"
        if "financial" in all_text or "bank" in all_text or "credit card" in all_text:
            return "financial_fraud"
        if "identity" in all_text or "ssn" in all_text:
            return "identity_theft"
        if "malware" in all_text or "download" in all_text:
            return "malware"
        if any(s.score >= 50 for s in input.signals):
            return "generic"
        return None

    @staticmethod
    def _generate_consequence(
        threat_level: ThreatLevel,
        scam_pattern: str | None,
        input: VerdictInput,
    ) -> str:
        if threat_level == ThreatLevel.SAFE:
            return ""

        if scam_pattern and scam_pattern in CONSEQUENCE_TEMPLATES:
            return CONSEQUENCE_TEMPLATES[scam_pattern]

        for signal in input.signals:
            if signal.source == SignalSource.LLM_REASONING and signal.detail:
                return signal.detail

        return CONSEQUENCE_TEMPLATES["generic"]

    @staticmethod
    def _generate_safe_action(scam_pattern: str | None, input: VerdictInput) -> str:
        pattern_to_action = {
            "phishing": "banking",
            "financial_fraud": "banking",
            "impersonation": "family",
            "identity_theft": "government",
            "malware": "tech_support",
            "gift_card_scam": "invoice",
        }

        action_key = pattern_to_action.get(scam_pattern or "", "generic")
        return SAFE_ACTION_TEMPLATES.get(action_key, SAFE_ACTION_TEMPLATES["generic"])

    @staticmethod
    def _generate_explanation(
        input: VerdictInput,
        threat_level: ThreatLevel,
        confidence: ConfidenceLevel,
    ) -> str:
        if threat_level == ThreatLevel.SAFE:
            if confidence == ConfidenceLevel.HIGH:
                return "We checked this against multiple sources and it appears safe. Always verify directly with the sender if you're unsure."
            return "This appears safe, but we recommend verifying with the sender through a trusted channel."

        high_signals = [s for s in input.signals if s.score >= 50]
        if high_signals:
            details = "; ".join(s.detail for s in high_signals[:3])
            return f"We found concerning indicators: {details}."

        if confidence == ConfidenceLevel.LOW:
            return "We don't have enough information to confirm this is safe. When in doubt, do not proceed."

        return "Some signals suggest this could be risky. We recommend caution."

    @staticmethod
    def _generate_summary(
        threat_level: ThreatLevel,
        confidence: ConfidenceLevel,
        scam_pattern: str | None,
    ) -> str:
        if threat_level == ThreatLevel.SAFE:
            if confidence == ConfidenceLevel.HIGH:
                return "This appears safe."
            return "This appears safe, but verify if unsure."

        if threat_level == ThreatLevel.DANGEROUS:
            pattern_labels = {
                "phishing": "This looks like a phishing attempt.",
                "sextortion": "This is a known sextortion scam pattern.",
                "pig_butchering": "This matches a romance-investment scam pattern.",
                "ransomware_bluff": "This appears to be a ransomware bluff email.",
                "impersonation": "This message appears to impersonate someone you know.",
                "gift_card_scam": "This is a gift card scam.",
                "financial_fraud": "This could lead to financial fraud.",
                "identity_theft": "This could lead to identity theft.",
                "malware": "This could contain malware.",
            }
            return pattern_labels.get(scam_pattern or "", "This looks dangerous. Do not proceed.")

        if confidence == ConfidenceLevel.LOW:
            return "We're not fully certain — proceed with caution."
        return "This looks suspicious. We recommend caution."
