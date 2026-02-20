from app.models.scan import ConfidenceLevel, SignalResult


def calibrate_confidence(signals: list[SignalResult]) -> tuple[ConfidenceLevel, float]:
    """Calibrate confidence level from aggregated signals.

    Rules:
    - High: multiple independent signal sources agree
    - Medium: some signals flag risk, others inconclusive
    - Low: limited signals available
    - Single-signal safe verdicts capped at Medium
    """
    if not signals:
        return ConfidenceLevel.LOW, 25.0

    source_types = {s.source for s in signals}
    scores = [s.score for s in signals]
    avg = sum(scores) / len(scores)
    max_score = max(scores)

    agreeing_high = sum(1 for s in scores if s >= 60)

    if len(source_types) >= 3 and agreeing_high >= 2:
        return ConfidenceLevel.HIGH, min(avg * 1.2, 95.0)

    if len(source_types) >= 2 and agreeing_high >= 1:
        return ConfidenceLevel.MEDIUM, min(max_score * 0.9, 80.0)

    if max_score >= 80:
        return ConfidenceLevel.MEDIUM, min(max_score * 0.85, 80.0)

    return ConfidenceLevel.LOW, min(avg, 55.0)
