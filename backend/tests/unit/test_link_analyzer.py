import pytest
from unittest.mock import AsyncMock, patch
from app.services.detection.link_analyzer import LinkAnalyzer
from app.models.scan import SignalSource

@pytest.fixture
def analyzer():
    return LinkAnalyzer()

@pytest.mark.asyncio
async def test_analyze_malformed_url(analyzer):
    # urlparse rarely throws exceptions for bad string formats, 
    # instead we mock it to force the exception block in analyzer.analyze()
    with patch("app.services.detection.link_analyzer.urlparse", side_effect=Exception("parse error")):
        result = await analyzer.analyze("http://invalid-url")
        assert len(result) == 1
        assert result[0].source == SignalSource.HEURISTIC
        assert result[0].detail == "Malformed URL"

@pytest.mark.asyncio
async def test_check_redirects_no_redirects(analyzer):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    
    mock_client_instance = AsyncMock()
    mock_client_instance.head.return_value = mock_resp
    
    mock_ac_cm = AsyncMock()
    mock_ac_cm.__aenter__.return_value = mock_client_instance
    
    with patch("app.services.detection.link_analyzer.httpx.AsyncClient", return_value=mock_ac_cm):
        signals = await analyzer._check_redirects("http://example.com")
        assert len(signals) == 0

@pytest.mark.asyncio
async def test_check_redirects_multiple_domains(analyzer):
    mock_resp_1 = AsyncMock()
    mock_resp_1.status_code = 301
    mock_resp_1.headers = {"location": "http://second.com"}
    
    mock_resp_2 = AsyncMock()
    mock_resp_2.status_code = 302
    mock_resp_2.headers = {"location": "http://third.com"}
    
    mock_resp_3 = AsyncMock()
    mock_resp_3.status_code = 301
    mock_resp_3.headers = {"location": "http://final.com"}
    
    mock_resp_final = AsyncMock()
    mock_resp_final.status_code = 200
    
    mock_client_instance = AsyncMock()
    mock_client_instance.head.side_effect = [mock_resp_1, mock_resp_2, mock_resp_3, mock_resp_final]
    
    mock_ac_cm = AsyncMock()
    mock_ac_cm.__aenter__.return_value = mock_client_instance
    
    with patch("app.services.detection.link_analyzer.httpx.AsyncClient", return_value=mock_ac_cm):
        signals = await analyzer._check_redirects("http://first.com")
        assert len(signals) >= 1
        assert any(s.source == SignalSource.REDIRECT_ANALYSIS for s in signals)

@pytest.mark.asyncio
async def test_check_domain_age_new(analyzer):
    mock_whois = AsyncMock()
    mock_whois.lookup.return_value = {"age_days": 10}
    
    with patch("app.integrations.whois_client.WhoisClient", return_value=mock_whois):
        signals = await analyzer._check_domain_age("http://example.com")
        assert len(signals) == 1
        assert signals[0].score == 75

@pytest.mark.asyncio
async def test_check_domain_age_medium(analyzer):
    mock_whois = AsyncMock()
    mock_whois.lookup.return_value = {"age_days": 60}
    
    with patch("app.integrations.whois_client.WhoisClient", return_value=mock_whois):
        signals = await analyzer._check_domain_age("http://example.com")
        assert len(signals) == 1
        assert signals[0].score == 50

@pytest.mark.asyncio
async def test_check_reputation_malicious(analyzer):
    mock_vt = AsyncMock()
    mock_vt.scan_url.return_value = {"positives": 5, "total": 90}
    
    mock_pt = AsyncMock()
    mock_pt.check_url.return_value = {"is_phish": True}
    
    mock_uh = AsyncMock()
    mock_uh.check_url.return_value = {"is_malware": True, "threat_type": "botnet"}
    
    with patch("app.integrations.virustotal.VirusTotalClient", return_value=mock_vt), \
         patch("app.integrations.phishtank.PhishTankClient", return_value=mock_pt), \
         patch("app.integrations.urlhaus.URLHausClient", return_value=mock_uh):
             
        signals = await analyzer._check_reputation("http://bad.com")
        assert len(signals) == 3
        assert any("PhishTank" in s.detail for s in signals)
        assert any("URLhaus" in s.detail for s in signals)
        assert any("threat intelligence sources" in s.detail for s in signals)
