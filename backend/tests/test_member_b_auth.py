"""
Unit and Integration Tests for Member B Authentication & Role-Based Authorization
Covers:
- Login success with valid credentials
- Login failure with incorrect password
- Verification that password_hash is never leaked in responses
- 401 Unauthorized for private routes without bearer token
- 403 Forbidden when USER role attempts to access admin-only endpoints
- 200 OK when ADMIN role accesses admin-only endpoints
- User registration and role enforcement
"""

import pytest
from backend.app.core.security import create_access_token


def test_login_success(client):
    """Verifies that a valid registered user receives a signed JWT access token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "priya@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "USER"
    assert "password" not in data
    assert "password_hash" not in data


def test_login_invalid_password_fails(client):
    """Verifies that an incorrect password raises HTTP 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "priya@example.com", "password": "wrongpassword!"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_password_hash_never_returned(client):
    """Ensures security: password_hash must never appear in response payloads."""
    # 1. Login response
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fitcheck.local", "password": "password123"},
    )
    assert "password_hash" not in login_res.text

    # 2. /me response
    token = login_res.json()["access_token"]
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert "password_hash" not in me_res.text
    assert me_res.json()["email"] == "admin@fitcheck.local"


def test_unauthenticated_request_fails(client):
    """Ensures private routes reject unauthenticated requests with HTTP 401."""
    response = client.get("/api/v1/reviews/mine")
    assert response.status_code == 401
    assert "Authentication credentials were not provided" in response.json()["detail"]


def test_user_forbidden_on_admin_endpoint(client):
    """Verifies RBAC: a normal USER accessing an ADMIN endpoint receives HTTP 403 Forbidden."""
    # Obtain token for normal USER (Priya, user_id=2)
    user_token = create_access_token(subject=2, role="USER")

    response = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert "ADMIN" in response.json()["detail"]


def test_admin_allowed_on_admin_endpoint(client):
    """Verifies RBAC: an ADMIN user accessing an ADMIN endpoint is allowed (HTTP 200)."""
    admin_token = create_access_token(subject=1, role="ADMIN")

    response = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_register_new_user(client):
    """Tests registration with duplicate check and role defaulting."""
    new_email = "testmemberb@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Member B Tester", "email": new_email, "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == new_email
    assert data["role"] == "USER"
    assert "password_hash" not in data

    # Attempting to register duplicate email must fail
    dup_res = client.post(
        "/api/v1/auth/register",
        json={"name": "Member B Tester 2", "email": new_email, "password": "anotherpassword"},
    )
    assert dup_res.status_code == 400
