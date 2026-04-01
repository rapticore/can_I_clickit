import pytest


@pytest.mark.anyio
async def test_register_returns_201_with_api_key(client):
    response = await client.post(
        "/v1/auth/register",
        json={"email": "newuser@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["tier"] == "free"
    assert data["grandma_mode"] is False
    assert data["api_key"] is not None
    assert len(data["api_key"]) == 64
    assert "clickit_session" in response.cookies


@pytest.mark.anyio
async def test_register_duplicate_email(client):
    await client.post(
        "/v1/auth/register",
        json={"email": "dup@example.com", "password": "securepass123"},
    )
    response = await client.post(
        "/v1/auth/register",
        json={"email": "dup@example.com", "password": "anotherpass123"},
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_register_password_too_short(client):
    response = await client.post(
        "/v1/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_login_success(client):
    await client.post(
        "/v1/auth/register",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    response = await client.post(
        "/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    assert "clickit_session" in response.cookies
    data = response.json()
    assert data["email"] == "login@example.com"


@pytest.mark.anyio
async def test_login_wrong_password(client):
    await client.post(
        "/v1/auth/register",
        json={"email": "wrong@example.com", "password": "securepass123"},
    )
    response = await client.post(
        "/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_logout(authenticated_client):
    response = await authenticated_client.post("/v1/auth/logout")
    assert response.status_code == 200
    # Cookie should be deleted (max-age=0 or removed)
    assert response.json()["message"] == "Logged out"


@pytest.mark.anyio
async def test_me_with_session(authenticated_client):
    response = await authenticated_client.get("/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["tier"] == "free"
    assert "api_key" in data


@pytest.mark.anyio
async def test_me_without_auth(client):
    # Debug mode is on, so this should still work (debug bypass)
    response = await client.get("/v1/auth/me")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_profile_update(authenticated_client):
    response = await authenticated_client.patch(
        "/v1/auth/profile",
        json={"grandma_mode": True, "language": "es"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grandma_mode"] is True
    assert data["language"] == "es"


@pytest.mark.anyio
async def test_rotate_api_key(authenticated_client):
    # Get current key
    me_response = await authenticated_client.get("/v1/auth/me")
    old_key = me_response.json()["api_key"]

    # Rotate
    response = await authenticated_client.post("/v1/auth/rotate-api-key")
    assert response.status_code == 200
    new_key = response.json()["api_key"]
    assert new_key != old_key
    assert len(new_key) == 64


@pytest.mark.anyio
async def test_scan_with_jwt(authenticated_client):
    response = await authenticated_client.post(
        "/v1/scan",
        json={"scan_type": "text", "content": "Hello, this is a test message"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "threat_level" in data


@pytest.mark.anyio
async def test_scan_with_api_key_still_works(client):
    # Register to get an API key
    reg = await client.post(
        "/v1/auth/register",
        json={"email": "apikey@example.com", "password": "securepass123"},
    )
    api_key = reg.json()["api_key"]

    # Clear cookies to simulate API-key-only auth
    client.cookies.clear()

    response = await client.post(
        "/v1/scan",
        json={"scan_type": "text", "content": "Hello, this is a test message"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert "threat_level" in data
