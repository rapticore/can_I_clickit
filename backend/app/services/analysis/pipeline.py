import structlog

from app.cache.redis_client import get_cached_verdict, hash_input, set_cached_verdict
from app.core.config import get_settings
from app.models.scan import (
    ScanRequest,
    ScanResult,
    ScanType,
    SignalResult,
)
from app.models.verdict import VerdictInput
from app.services.analysis.fast_path import FastPathAnalyzer
from app.services.analysis.llm_path import LLMAnalyzer
from app.services.analysis.ml_path import MLPathAnalyzer
from app.services.detection.content_analyzer import ContentAnalyzer
from app.services.detection.intent import IntentDetector
from app.services.detection.link_analyzer import LinkAnalyzer
from app.services.detection.qr_scanner import QRScanner
from app.services.detection.screenshot_ocr import ScreenshotOCR
from app.services.verdict.engine import VerdictEngine

logger = structlog.get_logger()

FAST_PATH_CONFIDENCE_THRESHOLD = 80.0
ML_PATH_CONFIDENCE_THRESHOLD = 70.0


class AnalysisPipeline:
    """Tiered analysis pipeline: Fast Path -> ML Path -> LLM Reasoning.

    60-70% of scans resolve on the fast path without LLM calls.
    """

    def __init__(self):
        self.fast_path = FastPathAnalyzer()
        self.ml_path = MLPathAnalyzer()
        self.llm_path = LLMAnalyzer()
        self.link_analyzer = LinkAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.intent_detector = IntentDetector()
        self.screenshot_ocr = ScreenshotOCR()
        self.qr_scanner = QRScanner()
        self.verdict_engine = VerdictEngine()

    async def analyze(self, scan_id: str, request: ScanRequest) -> ScanResult:
        content, extracted_urls = await self._normalize_input(request)

        cache_key = hash_input(content)
        cached = await get_cached_verdict(cache_key)
        if cached:
            logger.info("cache_hit", scan_id=scan_id)
            return ScanResult(scan_id=scan_id, **cached)

        all_signals: list[SignalResult] = []
        analysis_tier = "fast_path"

        fast_signals, fast_score = await self.fast_path.analyze(
            content=content,
            urls=extracted_urls,
            scan_type=request.scan_type,
        )
        all_signals.extend(fast_signals)

        if fast_score >= FAST_PATH_CONFIDENCE_THRESHOLD:
            logger.info("fast_path_resolved", scan_id=scan_id, score=fast_score)
        else:
            analysis_tier = "ml_path"
            ml_signals, ml_score = await self.ml_path.analyze(
                content=content,
                urls=extracted_urls,
                scan_type=request.scan_type,
            )
            all_signals.extend(ml_signals)
            combined_score = max(fast_score, ml_score)

            if combined_score >= ML_PATH_CONFIDENCE_THRESHOLD:
                logger.info("ml_path_resolved", scan_id=scan_id, score=combined_score)
            else:
                analysis_tier = "llm_reasoning"
                llm_signals, _llm_explanation = await self.llm_path.analyze(
                    content=content,
                    urls=extracted_urls,
                    scan_type=request.scan_type,
                    prior_signals=all_signals,
                )
                all_signals.extend(llm_signals)

        # Lightweight semantic detectors always run to enrich explanation quality.
        if content:
            content_signals = self.content_analyzer.analyze(content=content, language=request.language)
            all_signals.extend(content_signals)
            all_signals.extend(self.intent_detector.detect(content))

        # Live URL intelligence is opt-in to keep tests and local runs deterministic.
        settings = get_settings()
        if settings.enable_live_link_checks and extracted_urls:
            max_urls = max(0, settings.max_live_url_lookups)
            for url in extracted_urls[:max_urls]:
                all_signals.extend(await self.link_analyzer.analyze(url))

        verdict_input = VerdictInput(
            signals=all_signals,
            raw_score=self._aggregate_score(all_signals),
            analysis_tier=analysis_tier,
            content_snippet=content[:200] if content else "",
        )

        verdict = self.verdict_engine.compute(verdict_input)

        result = ScanResult(
            scan_id=scan_id,
            scan_type=request.scan_type,
            threat_level=verdict.threat_level,
            confidence=verdict.confidence,
            confidence_score=verdict.confidence_score,
            verdict_summary=verdict.verdict_summary,
            consequence_warning=verdict.consequence_warning,
            safe_action_suggestion=verdict.safe_action_suggestion,
            explanation=verdict.explanation,
            signals=all_signals,
            scam_pattern=verdict.scam_pattern,
            analysis_tier=analysis_tier,
        )

        await set_cached_verdict(cache_key, result.model_dump(mode="json", exclude={"scan_id", "created_at", "latency_ms"}))

        return result

    async def _normalize_input(self, request: ScanRequest) -> tuple[str, list[str]]:
        content = request.content or ""
        urls: list[str] = []

        if request.scan_type == ScanType.SCREENSHOT and request.image_base64:
            ocr_text, ocr_urls = await self.screenshot_ocr.extract(request.image_base64)
            content = ocr_text
            urls = ocr_urls

        elif request.scan_type in {ScanType.QR_CODE, ScanType.QR} and request.image_base64:
            qr_data = await self.qr_scanner.decode(request.image_base64)
            content = qr_data
            if qr_data.startswith(("http://", "https://")):
                urls = [qr_data]

        elif request.scan_type == ScanType.URL and content:
            urls = [content]

        else:
            urls = self._extract_urls(content)

        return content, urls

    @staticmethod
    def _extract_urls(text: str) -> list[str]:
        import re
        url_pattern = re.compile(
            r'https?://[^\s<>"\')\]]+',
            re.IGNORECASE,
        )
        return url_pattern.findall(text)

    @staticmethod
    def _aggregate_score(signals: list[SignalResult]) -> float:
        if not signals:
            return 50.0
        return sum(s.score for s in signals) / len(signals)
