import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.security import get_current_user
from app.models.recovery import (
    RecoveryChecklist,
    ThreatCategory,
    TriageAnswer,
    TriageRequest,
)
from app.services.compat import normalized_triage_answers
from app.services.recovery.engine import RecoveryEngine

router = APIRouter()
logger = structlog.get_logger()


def _extract_triage_answers(payload: Any) -> list[TriageAnswer]:
    if isinstance(payload, dict):
        if "answers" in payload:
            try:
                parsed = TriageRequest.model_validate(payload)
                answers = parsed.normalized_answers()
                if answers:
                    return answers
            except Exception:
                pass

            raw_answers = payload.get("answers")
            if isinstance(raw_answers, list):
                normalized = normalized_triage_answers(raw_answers)
                return [TriageAnswer.model_validate(item) for item in normalized]

        if "question_id" in payload and "selected_option_id" in payload:
            try:
                return [TriageAnswer.model_validate(payload)]
            except Exception:
                return []

    if isinstance(payload, list):
        try:
            parsed = [TriageAnswer.model_validate(item) for item in payload]
            if parsed:
                return parsed
        except Exception:
            pass

        normalized = normalized_triage_answers([item for item in payload if isinstance(item, dict)])
        return [TriageAnswer.model_validate(item) for item in normalized]

    return []


@router.post("/recovery/triage", response_model=RecoveryChecklist)
async def triage_recovery(
    raw_request: Request,
    _current_user=Depends(get_current_user),
):
    session_id = str(uuid.uuid4())
    logger.info("recovery_triage_started", session_id=session_id)

    engine = RecoveryEngine()
    try:
        payload = await raw_request.json()
    except Exception:
        payload = None

    answers = _extract_triage_answers(payload)

    if not answers:
        raise HTTPException(status_code=400, detail="At least one triage answer is required")

    category = engine.classify_from_triage(answers)
    checklist = engine.get_checklist(category)

    logger.info(
        "recovery_triage_completed",
        session_id=session_id,
        category=category.value,
    )

    return checklist


@router.get("/recovery/checklist/{category}", response_model=RecoveryChecklist)
async def get_recovery_checklist(
    category: str,
    _current_user=Depends(get_current_user),
):
    try:
        threat_cat = ThreatCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown category: {category}. Valid categories: {[c.value for c in ThreatCategory]}",
        )

    engine = RecoveryEngine()
    return engine.get_checklist(threat_cat)


@router.get("/recovery/triage/questions")
async def get_triage_questions(
    _current_user=Depends(get_current_user),
):
    engine = RecoveryEngine()
    return {"questions": engine.get_triage_questions()}
