import pytest
from unittest.mock import AsyncMock, patch
from app.integrations.virustotal import VirusTotalClient

@pytest.fixture
def mock_vt_settings():
    class Settings:
        virustotal_api_key = "vt_test_key"
    return Settings()

@pytest.fixture
def vt_client():
    return VirusTotalClient()

@pytest.mark.asyncio
async def test_virustotal_missing_api_key(vt_client):
    class NoKeySettings:
        virustotal_api_key = None
        
    with patch("app.integrations.virustotal.get_settings", return_value=NoKeySettings()):
        result = await vt_client.scan_url("http://example.com")
        assert result is None

@pytest.mark.asyncio
async def test_virustotal_scan_url_success(vt_client, mock_vt_settings):
    with patch("app.integrations.virustotal.get_settings", return_value=mock_vt_settings):
        # We need mock_resp.json() to NOT be async since it's just a regular method
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 2,
                        "suspicious": 1,
                        "harmless": 10,
                        "undetected": 5,
                        "timeout": 0
                    }
                }
            }
        }
        
        # mock_client_instance.get() needs to return a coroutine that resolves to mock_resp
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_resp
        
        mock_ac_cm = AsyncMock()
        mock_ac_cm.__aenter__.return_value = mock_client_instance
        
        with patch("app.integrations.virustotal.httpx.AsyncClient", return_value=mock_ac_cm):
            result = await vt_client.scan_url("http://google.com")
            assert result is not None
            assert result["positives"] == 3
            assert result["total"] == 18
            assert "raw_stats" in result

@pytest.mark.asyncio
async def test_virustotal_scan_url_404(vt_client, mock_vt_settings):
    with patch("app.integrations.virustotal.get_settings", return_value=mock_vt_settings):
        mock_resp = AsyncMock()
        mock_resp.status_code = 404
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_resp
        
        mock_ac_cm = AsyncMock()
        mock_ac_cm.__aenter__.return_value = mock_client_instance
        
        with patch("app.integrations.virustotal.httpx.AsyncClient", return_value=mock_ac_cm):
            result = await vt_client.scan_url("http://unknown.com")
            assert result is not None
            assert result["positives"] == 0
            assert result["total"] == 0

@pytest.mark.asyncio
async def test_virustotal_scan_url_403(vt_client, mock_vt_settings):
    with patch("app.integrations.virustotal.get_settings", return_value=mock_vt_settings):
        # Testing the basic "logger.warning" branch which returns None
        mock_resp = AsyncMock()
        mock_resp.status_code = 403
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_resp
        mock_ac_cm = AsyncMock()
        mock_ac_cm.__aenter__.return_value = mock_client_instance
        
        with patch("app.integrations.virustotal.httpx.AsyncClient", return_value=mock_ac_cm):
            result = await vt_client.scan_url("http://forbidden.com")
            assert result is None

@pytest.mark.asyncio
async def test_virustotal_scan_url_exception(vt_client, mock_vt_settings):
    with patch("app.integrations.virustotal.get_settings", return_value=mock_vt_settings):
        mock_ac_cm = AsyncMock()
        mock_ac_cm.__aenter__.side_effect = Exception("Network Error")
        
        with patch("app.integrations.virustotal.httpx.AsyncClient", return_value=mock_ac_cm):
            result = await vt_client.scan_url("http://error.com")
            assert result is None
