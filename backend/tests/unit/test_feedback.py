import pytest


@pytest.mark.asyncio
async def test_submit_feedback_correct(client):
    resp = await client.post(
        "/v1/feedback",
        json={
            "scan_id": "test-scan-123",
            "user_verdict": "correct",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["acknowledged"] is True
    assert data["scan_id"] == "test-scan-123"
    assert data["feedback_id"]


@pytest.mark.asyncio
async def test_submit_feedback_false_negative(client):
    resp = await client.post(
        "/v1/feedback",
        json={
            "scan_id": "test-scan-456",
            "user_verdict": "incorrect_false_negative",
            "comment": "This was actually a scam",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["acknowledged"] is True


@pytest.mark.asyncio
async def test_submit_feedback_false_positive(client):
    resp = await client.post(
        "/v1/feedback",
        json={
            "scan_id": "test-scan-789",
            "user_verdict": "incorrect_false_positive",
        },
    )
    assert resp.status_code == 200
