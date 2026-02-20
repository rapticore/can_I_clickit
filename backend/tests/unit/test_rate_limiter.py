import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.core.rate_limiter import check_rate_limit
from app.db.database import get_db

@pytest.mark.asyncio
async def test_rate_limiter_free_tier(mock_redis):
    # Temporarily remove dependency overrides from conftest to test rate limit
    app.dependency_overrides.clear()
    
    with patch("app.cache.redis_client.get_redis", return_value=mock_redis), \
         patch("app.main.init_db_schema", return_value=None):
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # We must set mock's get return to high value to trigger 429
            mock_redis.get.return_value = "51"
            
            resp = await client.post("/v1/scan", json={"content": "test", "scan_type": "text"})
            assert resp.status_code == 429
            assert "Free tier limit" in resp.json()["detail"]

@pytest.mark.asyncio
async def test_rate_limiter_premium_bypass(mock_redis):
    app.dependency_overrides.clear()
    
    with patch("app.cache.redis_client.get_redis", return_value=mock_redis), \
         patch("app.main.init_db_schema", return_value=None), \
         patch("app.core.rate_limiter.getattr", side_effect=lambda obj, name, default: "premium" if name == "user_tier" else default):
         
        mock_redis.get.return_value = "100" # Way over limit but shouldn't matter for premium
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/v1/scan", json={"content": "test", "scan_type": "text"})
            assert resp.status_code == 200
