from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from app.models.feedback import FeedbackVerdict
from app.models.scan import ScanResult, ThreatLevel


def legacy_risk_level(threat_level: ThreatLevel, confidence_score: float) -> str:
    """Map canonical threat levels to legacy 5-level risk strings."""
    if threat_level == ThreatLevel.SAFE:
        return "safe" if confidence_score >= 60 else "low"
    if threat_level == ThreatLevel.SUSPICIOUS:
        return "medium"
    if confidence_score >= 85:
        return "critical"
    return "high"


def build_legacy_scan_payload(result: ScanResult) -> dict[str, Any]:
    risk = legacy_risk_level(result.threat_level, result.confidence_score)
    return {
        "id": result.scan_id,
        "scan_id": result.scan_id,
        "scan_type": result.scan_type.value,
        "scanned_at": result.created_at.isoformat(),
        "threat_level": result.threat_level.value,
        "verdict": risk,
        "confidence": result.confidence.value,
        "confidence_score": result.confidence_score,
        "summary": result.verdict_summary,
        "verdict_summary": result.verdict_summary,
        "plain_language_summary": result.explanation,
        "explanation": result.explanation,
        "consequence_warning": result.consequence_warning,
        "consequences": result.consequence_warning,
        "safe_action_suggestion": result.safe_action_suggestion,
        "safe_action": result.safe_action_suggestion,
        "signals": [signal.model_dump(mode="json") for signal in result.signals],
        "scam_pattern": result.scam_pattern,
        "analysis_tier": result.analysis_tier,
        "latency_ms": result.latency_ms,
        "disclaimer": result.disclaimer,
    }


def build_extension_trust(scan_result: ScanResult, url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    domain = parsed.hostname or url
    risk = legacy_risk_level(scan_result.threat_level, scan_result.confidence_score)
    score = max(0, 100 - int(scan_result.confidence_score if risk in {"high", "critical"} else 100 - scan_result.confidence_score))
    return {
        "score": score,
        "verdict": risk,
        "confidence": scan_result.confidence.value,
        "domain": domain,
        "domain_age_days": None,
        "ssl_valid": parsed.scheme == "https",
        "last_scanned": datetime.utcnow().isoformat(),
        "summary": scan_result.verdict_summary,
        "signals": [signal.model_dump(mode="json") for signal in scan_result.signals],
    }


def normalize_feedback_verdict(payload: dict[str, Any]) -> FeedbackVerdict:
    direct = payload.get("user_verdict")
    if isinstance(direct, str):
        try:
            return FeedbackVerdict(direct)
        except ValueError:
            pass

    # Legacy clients may send booleans.
    if isinstance(payload.get("accurate"), bool):
        return FeedbackVerdict.CORRECT if payload["accurate"] else FeedbackVerdict.INCORRECT_FALSE_NEGATIVE
    if isinstance(payload.get("is_helpful"), bool):
        return FeedbackVerdict.CORRECT if payload["is_helpful"] else FeedbackVerdict.INCORRECT_FALSE_NEGATIVE

    return FeedbackVerdict.CORRECT


def normalized_triage_answers(raw_answers: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for answer in raw_answers:
        qid = str(answer.get("question_id", "")).strip()
        if not qid:
            continue

        selected = answer.get("selected_option_id")
        if isinstance(selected, str) and selected:
            normalized.append({"question_id": qid, "selected_option_id": selected})
            continue

        answer_ids = answer.get("answer_ids")
        if isinstance(answer_ids, list):
            first = next((opt for opt in answer_ids if isinstance(opt, str) and opt), None)
            if first:
                normalized.append({"question_id": qid, "selected_option_id": first})
    return normalized
