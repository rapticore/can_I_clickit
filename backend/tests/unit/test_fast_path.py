import pytest

from app.services.analysis.fast_path import FastPathAnalyzer


class TestFastPathAnalyzer:
    def setup_method(self):
        self.analyzer = FastPathAnalyzer()

    @pytest.mark.asyncio
    async def test_urgency_language_detection(self):
        signals, score = await self.analyzer.analyze(
            content="URGENT: Your account will be suspended immediately if you don't verify within 24 hours.",
            urls=[],
            scan_type="text",
        )
        assert score > 30
        assert any("urgency" in s.detail.lower() for s in signals)

    @pytest.mark.asyncio
    async def test_impersonation_detection(self):
        signals, score = await self.analyzer.analyze(
            content="Hey mom, I lost my phone, this is my new number",
            urls=[],
            scan_type="text",
        )
        assert any("impersonation" in s.detail.lower() for s in signals)

    @pytest.mark.asyncio
    async def test_financial_request_detection(self):
        signals, score = await self.analyzer.analyze(
            content="Please send money via gift card code immediately",
            urls=[],
            scan_type="text",
        )
        assert any("financial" in s.detail.lower() for s in signals)

    @pytest.mark.asyncio
    async def test_sextortion_detection(self):
        signals, score = await self.analyzer.analyze(
            content="I have compromising video footage from your webcam. Pay bitcoin to this wallet address or I will send it to all your contacts.",
            urls=[],
            scan_type="text",
        )
        assert any("sextortion" in s.detail.lower() for s in signals)

    @pytest.mark.asyncio
    async def test_pig_butchering_detection(self):
        signals, score = await self.analyzer.analyze(
            content="This exclusive crypto trading platform has guaranteed risk-free 100% profit returns. Deposit a fee to unlock your funds.",
            urls=[],
            scan_type="text",
        )
        assert any("pig_butchering" in s.detail.lower() for s in signals)

    @pytest.mark.asyncio
    async def test_known_safe_domain(self):
        signals, score = await self.analyzer.analyze(
            content="",
            urls=["https://www.google.com/search?q=test"],
            scan_type="url",
        )
        assert any("safe" in s.detail.lower() for s in signals)

    @pytest.mark.asyncio
    async def test_suspicious_tld(self):
        signals, score = await self.analyzer.analyze(
            content="",
            urls=["https://example.xyz/login"],
            scan_type="url",
        )
        assert any("suspicious tld" in s.detail.lower() for s in signals)

    @pytest.mark.asyncio
    async def test_typosquatting_detection(self):
        signals, score = await self.analyzer.analyze(
            content="",
            urls=["https://goggle.com/login"],
            scan_type="url",
        )
        assert any("typosquatting" in s.detail.lower() for s in signals)

    @pytest.mark.asyncio
    async def test_benign_message_low_score(self):
        signals, score = await self.analyzer.analyze(
            content="Hey, are we still meeting for lunch tomorrow?",
            urls=[],
            scan_type="text",
        )
        assert score < 50

    @pytest.mark.asyncio
    async def test_non_https_url(self):
        signals, score = await self.analyzer.analyze(
            content="",
            urls=["http://example.com/page"],
            scan_type="url",
        )
        assert any("non-https" in s.detail.lower() for s in signals)
