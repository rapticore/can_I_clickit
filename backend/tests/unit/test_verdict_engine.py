import pytest

from app.models.scan import ConfidenceLevel, SignalResult, SignalSource, ThreatLevel
from app.models.verdict import VerdictInput
from app.services.verdict.engine import VerdictEngine


class TestVerdictEngine:
    def setup_method(self):
        self.engine = VerdictEngine()

    def test_dangerous_verdict_on_high_score(self):
        input = VerdictInput(
            signals=[
                SignalResult(source=SignalSource.BLOCKLIST, score=90, detail="Known phishing URL"),
                SignalResult(source=SignalSource.ML_CLASSIFIER, score=85, detail="Phishing classifier high"),
                SignalResult(source=SignalSource.INTENT_DETECTION, score=80, detail="Social engineering intent"),
            ],
            raw_score=85.0,
        )
        result = self.engine.compute(input)
        assert result.threat_level == ThreatLevel.DANGEROUS
        assert result.confidence == ConfidenceLevel.HIGH

    def test_safe_verdict_on_low_score(self):
        input = VerdictInput(
            signals=[
                SignalResult(source=SignalSource.BLOCKLIST, score=5, detail="Known safe domain"),
                SignalResult(source=SignalSource.SSL_CHECK, score=5, detail="Valid SSL"),
                SignalResult(source=SignalSource.DOMAIN_AGE, score=5, detail="Domain > 10 years old"),
            ],
            raw_score=5.0,
        )
        result = self.engine.compute(input)
        assert result.threat_level == ThreatLevel.SAFE

    def test_safety_bias_low_confidence_defaults_to_suspicious(self):
        """Emergency confidence override: low confidence never produces 'safe'."""
        input = VerdictInput(
            signals=[
                SignalResult(source=SignalSource.HEURISTIC, score=20, detail="Single weak signal"),
            ],
            raw_score=20.0,
        )
        result = self.engine.compute(input)
        if result.confidence == ConfidenceLevel.LOW:
            assert result.threat_level != ThreatLevel.SAFE

    def test_suspicious_verdict_on_medium_score(self):
        input = VerdictInput(
            signals=[
                SignalResult(source=SignalSource.HEURISTIC, score=55, detail="Urgency language"),
                SignalResult(source=SignalSource.ML_CLASSIFIER, score=50, detail="Moderate phishing score"),
            ],
            raw_score=52.5,
        )
        result = self.engine.compute(input)
        assert result.threat_level == ThreatLevel.SUSPICIOUS

    def test_consequence_warning_for_phishing(self):
        input = VerdictInput(
            signals=[
                SignalResult(source=SignalSource.ML_CLASSIFIER, score=80, detail="Phishing detected"),
                SignalResult(source=SignalSource.INTENT_DETECTION, score=75, detail="Intent: credential theft"),
                SignalResult(source=SignalSource.BLOCKLIST, score=70, detail="Known phishing domain"),
            ],
            raw_score=75.0,
            content_snippet="verify your bank account credentials phishing",
        )
        result = self.engine.compute(input)
        assert result.consequence_warning != ""
        assert result.safe_action_suggestion != ""

    def test_no_signals_returns_low_confidence(self):
        input = VerdictInput(signals=[], raw_score=50.0)
        result = self.engine.compute(input)
        assert result.confidence == ConfidenceLevel.LOW

    def test_verdict_includes_disclaimer_fields(self):
        input = VerdictInput(
            signals=[
                SignalResult(source=SignalSource.HEURISTIC, score=60, detail="Test"),
            ],
            raw_score=60.0,
        )
        result = self.engine.compute(input)
        assert result.verdict_summary
        assert result.explanation

    def test_sextortion_pattern_detection(self):
        input = VerdictInput(
            signals=[
                SignalResult(source=SignalSource.HEURISTIC, score=80, detail="sextortion_pattern detected"),
            ],
            raw_score=80.0,
            content_snippet="compromising video webcam bitcoin wallet",
        )
        result = self.engine.compute(input)
        assert result.scam_pattern is not None

    def test_pig_butchering_pattern_detection(self):
        input = VerdictInput(
            signals=[
                SignalResult(source=SignalSource.HEURISTIC, score=80, detail="pig_butchering_pattern detected"),
            ],
            raw_score=80.0,
            content_snippet="guaranteed investment crypto platform returns",
        )
        result = self.engine.compute(input)
        assert result.scam_pattern is not None
