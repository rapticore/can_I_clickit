import pytest
from unittest.mock import patch, AsyncMock

import pytest
from app.models.scan import ConfidenceLevel, ScanType, ThreatLevel


@pytest.mark.asyncio
async def test_scan_text_suspicious(client):
    resp = await client.post(
        "/v1/scan",
        json={
            "content": "URGENT: Your bank account has been suspended. Click here immediately to verify your identity or your account will be closed within 24 hours.",
            "scan_type": "text",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["threat_level"] in ("suspicious", "dangerous")
    assert data["confidence"] in ("high", "medium", "low")
    assert data["verdict_summary"]
    assert data["consequence_warning"]
    assert data["safe_action_suggestion"]
    assert data["disclaimer"]


@pytest.mark.asyncio
async def test_scan_safe_url(client):
    resp = await client.post(
        "/v1/scan",
        json={
            "content": "https://www.google.com",
            "scan_type": "url",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["scan_type"] == "url"
    assert "threat_level" in data


@pytest.mark.asyncio
async def test_scan_sextortion_pattern(client):
    resp = await client.post(
        "/v1/scan",
        json={
            "content": "I have compromising video footage from your webcam. Send 0.5 bitcoin to this wallet address or I will release it to all your contacts and family.",
            "scan_type": "text",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["threat_level"] in ("suspicious", "dangerous")


@pytest.mark.asyncio
async def test_scan_pig_butchering_pattern(client):
    resp = await client.post(
        "/v1/scan",
        json={
            "content": "I found this amazing crypto trading platform with guaranteed 100% profit returns. It's a risk-free exclusive investment opportunity. You just need to deposit a fee to unlock your funds.",
            "scan_type": "text",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["threat_level"] in ("suspicious", "dangerous")


@pytest.mark.asyncio
async def test_scan_impersonation_pattern(client):
    resp = await client.post(
        "/v1/scan",
        json={
            "content": "Hey mom, I lost my phone and this is my new number. Can you send $200 via gift card? I'm in trouble and need help urgently.",
            "scan_type": "text",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["threat_level"] in ("suspicious", "dangerous")


@pytest.mark.asyncio
async def test_scan_benign_message(client):
    resp = await client.post(
        "/v1/scan",
        json={
            "content": "Hey, are we still meeting for lunch tomorrow at noon?",
            "scan_type": "text",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["threat_level"] in ("safe", "suspicious")


@pytest.mark.asyncio
async def test_scan_missing_content(client):
    resp = await client.post(
        "/v1/scan",
        json={
            "scan_type": "text",
        },
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scan_returns_required_fields(client):
    resp = await client.post(
        "/v1/scan",
        json={
            "content": "Test message",
            "scan_type": "text",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    required_fields = [
        "scan_id", "scan_type", "threat_level", "confidence",
        "confidence_score", "verdict_summary", "consequence_warning",
        "safe_action_suggestion", "explanation", "disclaimer",
    ]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

@pytest.mark.asyncio
async def test_scan_screenshot_file_upload_success(client):
    import base64
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    files = {"file": ("test.png", fake_png, "image/png")}
    data = {"language": "en"}
    resp = await client.post("/v1/scan/screenshot", data=data, files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["scan_type"] == "screenshot"


@pytest.mark.asyncio
async def test_scan_screenshot_missing_file(client):
    resp = await client.post("/v1/scan/screenshot", data={"language": "en"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_scan_screenshot_base64_success(client):
    resp = await client.post(
        "/v1/scan/screenshot/base64",
        json={
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            "language": "en",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["scan_type"] == "screenshot"


@pytest.mark.asyncio
async def test_scan_screenshot_base64_missing_image(client):
    resp = await client.post(
        "/v1/scan/screenshot/base64",
        json={"language": "en", "image_base64": ""},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_scan_history_pagination(client):
    await client.post(
        "/v1/scan",
        json={"content": "Test history 1", "scan_type": "text"},
    )
    await client.post(
        "/v1/scan",
        json={"content": "Test history 2", "scan_type": "text"},
    )

    resp = await client.get("/v1/scan/history?limit=10&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 2
    assert len(data["items"]) >= 2
    assert data["limit"] == 10
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_page_trust_endpoint(client):
    resp = await client.get("/v1/page-trust?url=https://www.google.com")
    assert resp.status_code == 200
    data = resp.json()
    assert "domain" in data
    assert "score" in data
    assert "verdict" in data


@pytest.mark.asyncio
async def test_legacy_extension_schema_scan(client):
    resp = await client.post(
        "/v1/scan",
        headers={"x-client-schema": "legacy"},
        json={
            "content": "Legacy schema test",
            "scan_type": "text",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "verdict_summary" in data
    assert "threat_level" in data
    assert "analysis_tier" in data
