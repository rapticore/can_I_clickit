import pytest
from unittest.mock import patch, AsyncMock

from app.models.scan import ScanRequest, ScanType, ThreatLevel
from app.services.analysis.pipeline import AnalysisPipeline


class TestAnalysisPipeline:
    def setup_method(self):
        self.pipeline = AnalysisPipeline()

    @pytest.mark.asyncio
    async def test_phishing_message_end_to_end(self):
        with patch("app.cache.redis_client.get_cached_verdict", return_value=None), \
             patch("app.cache.redis_client.set_cached_verdict", new_callable=AsyncMock):
            request = ScanRequest(
                content="URGENT: Your Bank of America account has been suspended. Click here immediately to verify your identity: http://bankofamerica-verify.xyz/login",
                scan_type=ScanType.TEXT,
            )
            result = await self.pipeline.analyze(scan_id="test-1", request=request)

            assert result.threat_level in (ThreatLevel.SUSPICIOUS, ThreatLevel.DANGEROUS)
            assert result.verdict_summary
            assert result.consequence_warning
            assert result.safe_action_suggestion
            assert len(result.signals) > 0

    @pytest.mark.asyncio
    async def test_safe_message_end_to_end(self):
        with patch("app.cache.redis_client.get_cached_verdict", return_value=None), \
             patch("app.cache.redis_client.set_cached_verdict", new_callable=AsyncMock):
            request = ScanRequest(
                content="Meeting is at 3pm in conference room B. See you there!",
                scan_type=ScanType.TEXT,
            )
            result = await self.pipeline.analyze(scan_id="test-2", request=request)

            assert result.scan_type == ScanType.TEXT
            assert result.verdict_summary
            assert result.disclaimer

    @pytest.mark.asyncio
    async def test_url_scan_end_to_end(self):
        with patch("app.cache.redis_client.get_cached_verdict", return_value=None), \
             patch("app.cache.redis_client.set_cached_verdict", new_callable=AsyncMock):
            request = ScanRequest(
                content="https://www.google.com",
                scan_type=ScanType.URL,
            )
            result = await self.pipeline.analyze(scan_id="test-3", request=request)
            assert result.scan_type == ScanType.URL

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached(self):
        cached_data = {
            "scan_type": "text",
            "threat_level": "safe",
            "confidence": "high",
            "confidence_score": 90.0,
            "verdict_summary": "Cached safe",
            "consequence_warning": "",
            "safe_action_suggestion": "No action needed",
            "explanation": "Previously analyzed as safe",
            "signals": [],
            "scam_pattern": None,
            "analysis_tier": "fast_path",
            "disclaimer": "Test disclaimer",
        }
        import json
        with patch("app.cache.redis_client.get_redis") as mock_redis_func:
            mock_redis = AsyncMock()
            mock_redis.get.return_value = json.dumps(cached_data)
            mock_redis_func.return_value = mock_redis
            request = ScanRequest(content="test", scan_type=ScanType.TEXT)
            result = await self.pipeline.analyze(scan_id="test-cache", request=request)
            assert result.verdict_summary == "Cached safe"

    @pytest.mark.asyncio
    async def test_multi_signal_phishing_high_confidence(self):
        with patch("app.cache.redis_client.get_cached_verdict", return_value=None), \
             patch("app.cache.redis_client.set_cached_verdict", new_callable=AsyncMock):
            request = ScanRequest(
                content="FINAL WARNING: Your Chase bank account will be terminated. Verify your identity immediately at http://chase-security.xyz/verify or face legal action within 24 hours. Your account has been locked due to unauthorized access.",
                scan_type=ScanType.TEXT,
            )
            result = await self.pipeline.analyze(scan_id="test-4", request=request)
            assert result.threat_level in (ThreatLevel.DANGEROUS, ThreatLevel.SUSPICIOUS)

    @pytest.mark.asyncio
    async def test_all_recovery_categories_accessible(self):
        from app.models.recovery import ThreatCategory
        from app.services.recovery.engine import RecoveryEngine

        engine = RecoveryEngine()
        for category in ThreatCategory:
            checklist = engine.get_checklist(category)
            assert checklist.category == category
            assert len(checklist.steps) > 0
            assert checklist.opening_message
            assert checklist.disclaimer
