import pytest
from unittest.mock import AsyncMock, patch
from app.integrations.anthropic_client import AnthropicClient

@pytest.fixture
def mock_settings():
    class Settings:
        anthropic_api_key = "test_key"
        anthropic_model_fast = "claude-test"
    return Settings()

@pytest.mark.asyncio
async def test_anthropic_client_initialization(mock_settings):
    with patch("app.integrations.anthropic_client.get_settings", return_value=mock_settings):
        with patch("anthropic.AsyncAnthropic") as mock_anthropic:
            client = AnthropicClient()
            api_client = await client._get_client()
            mock_anthropic.assert_called_once_with(api_key="test_key")
            assert client._client is not None
            
            # Subsequence calls use cached client
            await client._get_client()
            mock_anthropic.assert_called_once()

@pytest.mark.asyncio
async def test_anthropic_client_missing_key():
    class BadSettings:
        anthropic_api_key = None
        
    with patch("app.integrations.anthropic_client.get_settings", return_value=BadSettings()):
        client = AnthropicClient()
        with pytest.raises(RuntimeError, match="Anthropic API key not configured"):
            await client._get_client()

@pytest.mark.asyncio
async def test_anthropic_analyze_success(mock_settings):
    with patch("app.integrations.anthropic_client.get_settings", return_value=mock_settings):
        with patch("anthropic.AsyncAnthropic") as mock_anthropic:
            mock_messages = AsyncMock()
            mock_create_result = AsyncMock()
            
            class MockText:
                text = "analysis result"
                
            mock_create_result.content = [MockText()]
            mock_messages.create.return_value = mock_create_result
            
            mock_instance = AsyncMock()
            mock_instance.messages = mock_messages
            mock_anthropic.return_value = mock_instance
            
            client = AnthropicClient()
            result = await client.analyze("system block", "user block")
            assert result == "analysis result"
            mock_messages.create.assert_called_once_with(
                model="claude-test",
                max_tokens=1024,
                system="system block",
                messages=[{"role": "user", "content": "user block"}]
            )

@pytest.mark.asyncio
async def test_anthropic_analyze_fails(mock_settings):
    with patch("app.integrations.anthropic_client.get_settings", return_value=mock_settings):
        with patch("anthropic.AsyncAnthropic") as mock_anthropic:
            mock_messages = AsyncMock()
            mock_messages.create.side_effect = Exception("API Error")
            
            mock_instance = AsyncMock()
            mock_instance.messages = mock_messages
            mock_anthropic.return_value = mock_instance
            
            client = AnthropicClient()
            with pytest.raises(Exception, match="API Error"):
                await client.analyze("system block", "user block")

@pytest.mark.asyncio
async def test_anthropic_client_close(mock_settings):
    client = AnthropicClient()
    client._client = "some mock"
    await client.close()
    assert client._client is None
