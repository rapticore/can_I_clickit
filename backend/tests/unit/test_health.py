import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert "checks" in data
    assert data["checks"]["api"] == "ok"
