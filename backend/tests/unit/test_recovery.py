import pytest

from app.models.recovery import ThreatCategory


@pytest.mark.asyncio
async def test_get_triage_questions(client):
    resp = await client.get("/v1/recovery/triage/questions")
    assert resp.status_code == 200
    data = resp.json()
    assert "questions" in data
    assert len(data["questions"]) > 0

    first_q = data["questions"][0]
    assert "id" in first_q
    assert "question" in first_q
    assert "options" in first_q
    assert len(first_q["options"]) >= 2


@pytest.mark.asyncio
async def test_triage_credential_theft(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json={
            "answers": [
                {"question_id": "q1", "selected_option_id": "q1_password"},
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "credential_theft"
    assert data["urgency"] == "high"
    assert data["title"] == "Password Compromised"
    assert len(data["steps"]) > 0
    assert data["opening_message"]
    assert data["disclaimer"]


@pytest.mark.asyncio
async def test_triage_financial_fraud(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json={
            "answers": [
                {"question_id": "q1", "selected_option_id": "q1_financial"},
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "financial_fraud"
    assert data["urgency"] == "critical"
    assert len(data["quick_dial_contacts"]) > 0


@pytest.mark.asyncio
async def test_triage_sextortion(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json={
            "answers": [
                {"question_id": "q1", "selected_option_id": "q1_threat"},
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "blackmail_sextortion"
    assert data["urgency"] == "medium"
    assert "do not pay" in data["steps"][0]["title"].lower()


@pytest.mark.asyncio
async def test_triage_pig_butchering(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json={
            "answers": [
                {"question_id": "q1", "selected_option_id": "q1_invest"},
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "pig_butchering"
    assert data["urgency"] == "critical"


@pytest.mark.asyncio
async def test_triage_link_then_password(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json={
            "answers": [
                {"question_id": "q1", "selected_option_id": "q1_link"},
                {"question_id": "q2_link", "selected_option_id": "q2_entered_pw"},
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "credential_theft"


@pytest.mark.asyncio
async def test_triage_legacy_answer_ids_payload(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json=[
            {"question_id": "q1", "answer_ids": ["q1_financial"]},
        ],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "financial_fraud"


@pytest.mark.asyncio
async def test_get_checklist_by_category(client):
    for category in ThreatCategory:
        resp = await client.get(f"/v1/recovery/checklist/{category.value}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == category.value
        assert len(data["steps"]) > 0
        assert data["disclaimer"]


@pytest.mark.asyncio
async def test_get_checklist_invalid_category(client):
    resp = await client.get("/v1/recovery/checklist/nonexistent")
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_triage_malformed_json_returns_400(client):
    resp = await client.post(
        "/v1/recovery/triage",
        content="not valid json",
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_triage_empty_answers_returns_400(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json={"answers": []}
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_triage_extract_answers_dict_single_question(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json={"question_id": "q1", "selected_option_id": "opt1"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "general_unknown"


@pytest.mark.asyncio
async def test_triage_extract_answers_list_of_dicts(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json=[{"question_id": "q1", "selected_option_id": "opt1"}]
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "general_unknown"


@pytest.mark.asyncio
async def test_triage_extract_answers_list_unparseable(client):
    resp = await client.post(
        "/v1/recovery/triage",
        json=["just a string", 123]
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_recovery_checklist_unknown_category(client):
    resp = await client.get("/v1/recovery/checklist/made_up_category")
    assert resp.status_code == 400
    assert "Unknown category" in resp.json()["detail"]
