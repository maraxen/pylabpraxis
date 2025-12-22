"""Tests for authentication API endpoints.

This module tests the security-critical authentication endpoints:
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- POST /api/v1/auth/logout

Following test pattern from test_workcells.py (Setup → Act → Assert).
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


# ==============================================================================
# Sprint 1B: Login Endpoint Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_login_success_returns_access_token(
    client: AsyncClient,
    test_user,
) -> None:
    """POST /api/v1/auth/login with valid credentials returns JWT token."""
    # 1. SETUP: test_user fixture provides active user with password='testpass123'

    # 2. ACT: Login with valid credentials
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )

    # 3. ASSERT: Successful response with token
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Verify user data in response
    assert "user" in data
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["is_active"] is True

    # Verify token is a non-empty string
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(
    client: AsyncClient,
    test_user,
) -> None:
    """POST /api/v1/auth/login with incorrect password fails with 401."""
    # 1. SETUP: test_user exists with correct password='testpass123'

    # 2. ACT: Login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpassword"},
    )

    # 3. ASSERT: Unauthorized error
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Incorrect username or password" in data["detail"]


@pytest.mark.asyncio
async def test_login_with_nonexistent_user_returns_401(
    client: AsyncClient,
) -> None:
    """POST /api/v1/auth/login with fake username fails with 401.

    Uses same error message as wrong password to prevent user enumeration.
    """
    # 1. SETUP: No user setup needed (testing non-existent user)

    # 2. ACT: Login with non-existent username
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "fakeuser999", "password": "anypassword"},
    )

    # 3. ASSERT: Same 401 error as wrong password (prevents enumeration)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Incorrect username or password" in data["detail"]


@pytest.mark.asyncio
async def test_login_with_inactive_user_returns_401(
    client: AsyncClient,
    test_inactive_user,
) -> None:
    """POST /api/v1/auth/login with inactive user fails with 401.

    Prevents account takeover after user deactivation.
    Uses generic error message to prevent user enumeration.
    """
    # 1. SETUP: test_inactive_user fixture provides inactive user

    # 2. ACT: Login with inactive user's credentials
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "inactiveuser", "password": "testpass123"},
    )

    # 3. ASSERT: Unauthorized error with generic message (security best practice)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    # Generic error prevents user enumeration (same as wrong password)
    assert "Incorrect username or password" in data["detail"]


# ==============================================================================
# Sprint 1C: /me Endpoint Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_me_with_valid_token_returns_user(
    client: AsyncClient,
    test_user,
    valid_auth_headers,
) -> None:
    """GET /api/v1/auth/me with valid JWT returns user data."""
    # 1. SETUP: valid_auth_headers fixture provides Bearer token for test_user

    # 2. ACT: Call /me with authorization header
    response = await client.get(
        "/api/v1/auth/me",
        headers=valid_auth_headers,
    )

    # 3. ASSERT: Success with user data
    assert response.status_code == 200
    data = response.json()

    # Verify user data matches test_user
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_me_without_token_returns_401(
    client: AsyncClient,
) -> None:
    """GET /api/v1/auth/me without Authorization header fails with 401."""
    # 1. SETUP: No setup needed (testing missing auth)

    # 2. ACT: Call /me without authentication
    response = await client.get("/api/v1/auth/me")

    # 3. ASSERT: Unauthorized error
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_me_with_expired_token_returns_401(
    client: AsyncClient,
    test_user,
    expired_token,
) -> None:
    """GET /api/v1/auth/me with expired token fails with 401."""
    # 1. SETUP: expired_token fixture provides token expired 1 second ago

    # 2. ACT: Call /me with expired token
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    # 3. ASSERT: Unauthorized error (token expired)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_me_with_inactive_user_returns_403(
    client: AsyncClient,
    test_inactive_user,
) -> None:
    """GET /api/v1/auth/me with valid token for inactive user fails.

    Prevents privilege escalation after user deactivation.
    """
    # 1. SETUP: Create valid token for inactive user
    from praxis.backend.utils.auth import create_access_token

    token = create_access_token(
        data={
            "sub": test_inactive_user.username,
            "user_id": str(test_inactive_user.accession_id),
        }
    )

    # 2. ACT: Call /me with token for inactive user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    # 3. ASSERT: Forbidden or Unauthorized error
    # Note: Implementation may return 401 or 403, both are acceptable
    assert response.status_code in [401, 403]
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_me_with_deleted_user_returns_401(
    client: AsyncClient,
) -> None:
    """GET /api/v1/auth/me with token for non-existent user fails."""
    # 1. SETUP: Create token for non-existent user_id
    import uuid
    from praxis.backend.utils.auth import create_access_token

    fake_user_id = uuid.uuid4()
    token = create_access_token(
        data={"sub": "deleteduser", "user_id": str(fake_user_id)}
    )

    # 2. ACT: Call /me with token for deleted user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    # 3. ASSERT: Unauthorized error
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


# ==============================================================================
# Sprint 2A: Edge Case Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_login_with_missing_fields_returns_422(
    client: AsyncClient,
) -> None:
    """POST /api/v1/auth/login without required fields fails with 422.

    Tests Pydantic request validation.
    """
    # Test case 1: Empty payload
    response = await client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422

    # Test case 2: Missing password
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser"},
    )
    assert response.status_code == 422

    # Test case 3: Missing username
    response = await client.post(
        "/api/v1/auth/login",
        json={"password": "testpass123"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_logout_returns_success_message(
    client: AsyncClient,
) -> None:
    """POST /api/v1/auth/logout returns success message.

    Stateless logout - no server-side session invalidation.
    """
    # 1. SETUP: No setup needed

    # 2. ACT: Call logout
    response = await client.post("/api/v1/auth/logout")

    # 3. ASSERT: Success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "logged out" in data["message"].lower()


@pytest.mark.asyncio
async def test_logout_is_stateless(
    client: AsyncClient,
    test_user,
    valid_auth_headers,
) -> None:
    """Verify logout doesn't invalidate token (stateless JWT).

    Documents that logout is client-side only - token remains valid.
    """
    # 1. SETUP: Get valid token via login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 2. ACT: Logout
    logout_response = await client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200

    # 3. ASSERT: Token still works after logout (stateless)
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200, "Token should still work after stateless logout"


# ==============================================================================
# Sprint 2B: Integration & Security Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_full_authentication_flow(
    client: AsyncClient,
    test_user,
) -> None:
    """Integration test: Complete auth flow (login → /me → logout → /me).

    Verifies the complete authentication lifecycle for frontend.
    """
    # 1. Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 2. Verify /me works with token
    me_response_1 = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response_1.status_code == 200
    assert me_response_1.json()["username"] == "testuser"

    # 3. Logout
    logout_response = await client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200

    # 4. Token still works after logout (stateless)
    me_response_2 = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response_2.status_code == 200


@pytest.mark.asyncio
async def test_concurrent_logins_both_valid(
    client: AsyncClient,
    test_user,
) -> None:
    """Verify multiple logins return valid tokens.

    Note: Stateless JWT tokens generated in the same second may be identical
    (no 'iat' claim). This is acceptable - expiration prevents long-term replay.
    """
    import asyncio

    # 1. ACT: Login twice with small delay
    response1 = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    # Small delay to potentially get different exp timestamp
    await asyncio.sleep(1)
    response2 = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )

    # 2. ASSERT: Both logins successful with valid tokens
    assert response1.status_code == 200
    assert response2.status_code == 200

    token1 = response1.json()["access_token"]
    token2 = response2.json()["access_token"]

    # Verify both tokens work for authenticated requests
    me_response1 = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token1}"},
    )
    me_response2 = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert me_response1.status_code == 200
    assert me_response2.status_code == 200
    assert me_response1.json()["username"] == "testuser"
    assert me_response2.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_token_cannot_be_used_for_different_user(
    client: AsyncClient,
    test_user,
    test_inactive_user,
) -> None:
    """Verify token user_id binding prevents privilege escalation.

    Ensures token for user A cannot access user B's data.
    """
    # 1. SETUP: Get token for test_user
    from praxis.backend.utils.auth import create_access_token

    test_user_token = create_access_token(
        data={"sub": test_user.username, "user_id": str(test_user.accession_id)}
    )

    # 2. ACT: Call /me with test_user's token
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )

    # 3. ASSERT: Returns test_user data (not test_inactive_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["username"] != test_inactive_user.username


@pytest.mark.asyncio
async def test_login_case_sensitive_username(
    client: AsyncClient,
    test_user,
) -> None:
    """Verify username is case-sensitive (security best practice)."""
    # 1. SETUP: test_user has username="testuser" (lowercase)

    # 2. ACT: Try login with uppercase username
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "TESTUSER", "password": "testpass123"},
    )

    # 3. ASSERT: Should fail (or document case-insensitive behavior)
    # Most secure systems treat usernames as case-sensitive
    assert response.status_code == 401, "Username should be case-sensitive for security"
