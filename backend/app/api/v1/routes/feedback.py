import uuid

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Feedback as FeedbackRow
from app.db.models import ScanMetadata, User
from app.models.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter()
logger = structlog.get_logger()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feedback_id = str(uuid.uuid4())

    scan = (await db.execute(select(ScanMetadata).where(ScanMetadata.id == request.scan_id))).scalar_one_or_none()
    if scan is None:
        # Legacy/mobile clients may submit feedback with non-persisted scan IDs.
        scan = ScanMetadata(
            id=request.scan_id,
            user_id=current_user.id,
            scan_type="text",
            verdict="suspicious",
            confidence="low",
            confidence_score=50.0,
            scam_pattern=None,
            analysis_tier="unknown",
            latency_ms=0,
        )
        db.add(scan)
        await db.commit()

    row = FeedbackRow(
        id=feedback_id,
        scan_id=request.scan_id,
        user_reported_verdict=request.user_verdict.value if request.user_verdict else "correct",
        comment=request.comment,
    )
    db.add(row)
    await db.commit()

    logger.info(
        "feedback_submitted",
        feedback_id=feedback_id,
        scan_id=request.scan_id,
        user_verdict=request.user_verdict.value if request.user_verdict else "correct",
    )

    return FeedbackResponse(
        feedback_id=feedback_id,
        scan_id=request.scan_id,
    )
