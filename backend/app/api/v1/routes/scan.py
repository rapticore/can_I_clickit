import time
import uuid
import hashlib
from typing import Any

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limiter import check_rate_limit
from app.core.security import verify_api_key
from app.db.database import get_db
from app.db.models import ScanMetadata, User
from app.models.scan import ScanRequest, ScanResult, ScanType
from app.services.compat import build_extension_trust, build_legacy_scan_payload
from app.services.analysis.pipeline import AnalysisPipeline

router = APIRouter()
logger = structlog.get_logger()


class ScreenshotScanBody(BaseModel):
    image_base64: str | None = None
    language: str = "en"


def _is_legacy_scan_request(raw_payload: dict[str, Any], headers: dict[str, str]) -> bool:
    if headers.get("x-client-schema", "").lower() == "legacy":
        return True
    if "type" in raw_payload:
        return True
    metadata = raw_payload.get("metadata")
    if isinstance(metadata, dict):
        if str(metadata.get("schema", "")).lower() == "legacy":
            return True
        if str(metadata.get("client", "")).lower() in {"legacy", "chrome-extension"}:
            return True
        # Legacy extension payloads include hover context metadata.
        if bool(metadata.get("hover_context")):
            return True
    return False


async def _get_or_create_user(db: AsyncSession, api_key: str) -> User:
    digest = hashlib.sha256(api_key.encode()).hexdigest()[:20]
    email = f"user-{digest}@local.clickit"
    existing = await db.execute(select(User).where(User.email == email))
    user = existing.scalar_one_or_none()
    if user:
        return user

    user = User(
        email=email,
        hashed_password="not-used",
        tier="free",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _persist_scan_result(db: AsyncSession, user_id: str, result: ScanResult) -> None:
    row = ScanMetadata(
        id=result.scan_id,
        user_id=user_id,
        scan_type=result.scan_type.value,
        verdict=result.threat_level.value,
        confidence=result.confidence.value,
        confidence_score=result.confidence_score,
        scam_pattern=result.scam_pattern,
        analysis_tier=result.analysis_tier,
        latency_ms=result.latency_ms,
    )
    db.add(row)
    await db.commit()


@router.post("/scan", response_model=ScanResult)
async def scan_content(
    raw_request: Request,
    request: ScanRequest,
    _api_key: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit),
    db: AsyncSession = Depends(get_db),
):
    scan_id = str(uuid.uuid4())
    start = time.perf_counter()

    logger.info(
        "scan_started",
        scan_id=scan_id,
        scan_type=request.scan_type.value,
    )

    pipeline = AnalysisPipeline()
    result = await pipeline.analyze(scan_id=scan_id, request=request)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    result.latency_ms = elapsed_ms

    logger.info(
        "scan_completed",
        scan_id=scan_id,
        threat_level=result.threat_level.value,
        confidence=result.confidence.value,
        tier=result.analysis_tier,
        latency_ms=elapsed_ms,
    )

    try:
        user = await _get_or_create_user(db, _api_key)
        await _persist_scan_result(db, user.id, result)
    except Exception as exc:
        logger.error("scan_persist_failed", scan_id=scan_id, error=str(exc))

    payload = {}
    try:
        payload = await raw_request.json()
    except Exception:
        payload = {}

    if _is_legacy_scan_request(payload if isinstance(payload, dict) else {}, dict(raw_request.headers)):
        return JSONResponse(content=build_legacy_scan_payload(result))

    return result


@router.post("/scan/screenshot", response_model=ScanResult)
async def scan_screenshot(
    raw_request: Request,
    file: UploadFile | None = File(None),
    language: str = Form("en"),
    _api_key: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit),
    db: AsyncSession = Depends(get_db),
):
    import base64

    scan_id = str(uuid.uuid4())
    start = time.perf_counter()

    image_b64 = ""
    if file is not None:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode()
    else:
        raise HTTPException(status_code=400, detail="Provide a screenshot file")

    request = ScanRequest(
        scan_type=ScanType.SCREENSHOT,
        image_base64=image_b64,
        language=language,
    )

    pipeline = AnalysisPipeline()
    result = await pipeline.analyze(scan_id=scan_id, request=request)
    result.latency_ms = int((time.perf_counter() - start) * 1000)

    try:
        user = await _get_or_create_user(db, _api_key)
        await _persist_scan_result(db, user.id, result)
    except Exception as exc:
        logger.error("scan_persist_failed", scan_id=scan_id, error=str(exc))

    payload = {}
    try:
        payload = await raw_request.json()
    except Exception:
        payload = {}
    if _is_legacy_scan_request(payload if isinstance(payload, dict) else {}, dict(raw_request.headers)):
        return JSONResponse(content=build_legacy_scan_payload(result))

    return result


@router.post("/scan/screenshot/base64", response_model=ScanResult)
async def scan_screenshot_base64(
    payload: ScreenshotScanBody,
    _api_key: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit),
    db: AsyncSession = Depends(get_db),
):
    if not payload.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required")

    scan_id = str(uuid.uuid4())
    start = time.perf_counter()
    request = ScanRequest(
        scan_type=ScanType.SCREENSHOT,
        image_base64=payload.image_base64,
        language=payload.language,
    )

    pipeline = AnalysisPipeline()
    result = await pipeline.analyze(scan_id=scan_id, request=request)
    result.latency_ms = int((time.perf_counter() - start) * 1000)

    try:
        user = await _get_or_create_user(db, _api_key)
        await _persist_scan_result(db, user.id, result)
    except Exception as exc:
        logger.error("scan_persist_failed", scan_id=scan_id, error=str(exc))

    return result


@router.get("/scan/history")
async def get_scan_history(
    _api_key: str = Depends(verify_api_key),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    user = await _get_or_create_user(db, _api_key)
    items_query = (
        select(ScanMetadata)
        .where(ScanMetadata.user_id == user.id)
        .order_by(desc(ScanMetadata.created_at))
        .limit(limit)
        .offset(offset)
    )
    rows = (await db.execute(items_query)).scalars().all()

    total_query = select(func.count()).select_from(ScanMetadata).where(ScanMetadata.user_id == user.id)
    total = int((await db.execute(total_query)).scalar() or 0)

    return {
        "items": [
            {
                "scan_id": row.id,
                "scan_type": row.scan_type,
                "threat_level": row.verdict,
                "confidence": row.confidence,
                "confidence_score": row.confidence_score,
                "scam_pattern": row.scam_pattern,
                "analysis_tier": row.analysis_tier,
                "latency_ms": row.latency_ms,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/page-trust")
async def get_page_trust(
    url: str = Query(..., min_length=4),
    _api_key: str = Depends(verify_api_key),
):
    scan_id = str(uuid.uuid4())
    pipeline = AnalysisPipeline()
    request = ScanRequest(content=url, scan_type=ScanType.URL)
    result = await pipeline.analyze(scan_id=scan_id, request=request)
    return build_extension_trust(result, url)
