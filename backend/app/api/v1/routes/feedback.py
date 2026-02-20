import uuid
import hashlib

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_api_key
from app.db.database import get_db
from app.db.models import Feedback as FeedbackRow
from app.db.models import ScanMetadata, User
from app.models.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter()
logger = structlog.get_logger()


async def _get_or_create_user(db: AsyncSession, api_key: str) -> User:
    digest = hashlib.sha256(api_key.encode()).hexdigest()[:20]
    email = f"user-{digest}@local.clickit"
    existing = await db.execute(select(User).where(User.email == email))
    user = existing.scalar_one_or_none()
    if user:
        return user

    user = User(email=email, hashed_password="not-used", tier="free")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    _api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    feedback_id = str(uuid.uuid4())
    user = await _get_or_create_user(db, _api_key)

    scan = (await db.execute(select(ScanMetadata).where(ScanMetadata.id == request.scan_id))).scalar_one_or_none()
    if scan is None:
        # Legacy/mobile clients may submit feedback with non-persisted scan IDs.
        scan = ScanMetadata(
            id=request.scan_id,
            user_id=user.id,
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
