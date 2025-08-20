"""Integration tests for Auth API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


class TestAuthEndpoints:
    """Test Auth API endpoints."""
    
    def test_health_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "Syria GPT" in data["service"]
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Welcome to Syria GPT" in data["message"]
        assert data["version"] == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_signup_success(self, client: TestClient, sample_user_data: dict):
        """Test successful user signup."""
        with patch('infrastructure.services.EmailService.send_verification_email', new_callable=AsyncMock):
            response = client.post("/auth/signup", json=sample_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "successfully" in data["message"].lower()
    
    def test_signup_invalid_email(self, client: TestClient):
        """Test signup with invalid email."""
        invalid_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "first_name": "Test"
        }
        
        response = client.post("/auth/signup", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_signup_short_password(self, client: TestClient):
        """Test signup with short password."""
        invalid_data = {
            "email": "test@example.com",
            "password": "short",
            "first_name": "Test"
        }
        
        response = client.post("/auth/signup", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client: TestClient, sample_user_data: dict):
        """Test signup with duplicate email."""
        # First signup
        with patch('infrastructure.services.EmailService.send_verification_email', new_callable=AsyncMock):
            client.post("/auth/signup", json=sample_user_data)
        
        # Second signup with same email
        with patch('infrastructure.services.EmailService.send_verification_email', new_callable=AsyncMock):
            response = client.post("/auth/signup", json=sample_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_signin_invalid_credentials(self, client: TestClient):
        """Test signin with invalid credentials."""
        signin_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/signin", json=signin_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower()
    
    def test_google_oauth_url(self, client: TestClient):
        """Test getting Google OAuth URL."""
        response = client.get("/auth/google")
        
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "google" in data.get("provider", "").lower()
        assert "accounts.google.com" in data["auth_url"]
    
    def test_facebook_oauth_url(self, client: TestClient):
        """Test getting Facebook OAuth URL."""
        response = client.get("/auth/facebook")
        
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "facebook" in data.get("provider", "").lower()
        assert "facebook.com" in data["auth_url"]
    
    def test_google_callback_invalid_code(self, client: TestClient):
        """Test Google OAuth callback with invalid code."""
        callback_data = {"code": "invalid_google_code"}
        
        response = client.post("/auth/google/callback", json=callback_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_facebook_callback_invalid_code(self, client: TestClient):
        """Test Facebook OAuth callback with invalid code."""
        callback_data = {"code": "invalid_facebook_code"}
        
        response = client.post("/auth/facebook/callback", json=callback_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_verify_email_invalid_token(self, client: TestClient):
        """Test email verification with invalid token."""
        verification_data = {"token": "invalid_token"}
        
        response = client.post("/auth/verify-email", json=verification_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()
    
    def test_me_endpoint_without_token(self, client: TestClient):
        """Test /me endpoint without authentication token."""
        response = client.get("/auth/me")
        
        assert response.status_code == 403  # Forbidden without token
    
    def test_me_endpoint_with_invalid_token(self, client: TestClient):
        """Test /me endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_change_password_without_token(self, client: TestClient):
        """Test change password without authentication token."""
        password_data = {
            "current_password": "currentpass",
            "new_password": "newpassword123"
        }
        
        response = client.post("/auth/change-password", json=password_data)
        
        assert response.status_code == 403  # Forbidden without token
    
    def test_change_password_invalid_current_password(self, client: TestClient, valid_access_token: str):
        """Test change password with invalid current password."""
        password_data = {
            "current_password": "wrongcurrentpass",
            "new_password": "newpassword123"
        }
        headers = {"Authorization": f"Bearer {valid_access_token}"}
        
        response = client.post("/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "invalid" in data["detail"].lower()
    
    def test_change_password_short_new_password(self, client: TestClient, valid_access_token: str):
        """Test change password with short new password."""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "short"
        }
        headers = {"Authorization": f"Bearer {valid_access_token}"}
        
        response = client.post("/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_endpoint_with_valid_token(self, client: TestClient, valid_access_token: str):
        """Test /me endpoint with valid token."""
        headers = {"Authorization": f"Bearer {valid_access_token}"}
        
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "status" in data


class TestAuthEndpointsWithRealAuth:
    """Test Auth endpoints with real authentication flow."""
    
    @pytest.mark.asyncio
    async def test_full_signup_signin_flow(self, client: TestClient):
        """Test complete signup and signin flow."""
        # Step 1: Signup
        signup_data = {
            "email": "flowtest@example.com",
            "password": "testpassword123",
            "first_name": "Flow",
            "last_name": "Test"
        }
        
        with patch('infrastructure.services.EmailService.send_verification_email', new_callable=AsyncMock):
            signup_response = client.post("/auth/signup", json=signup_data)
        
        assert signup_response.status_code == 200
        
        # Step 2: Signin (might fail if email not verified, depending on business logic)
        signin_data = {
            "email": "flowtest@example.com",
            "password": "testpassword123"
        }
        
        signin_response = client.post("/auth/signin", json=signin_data)
        
        # Could be 200 (success) or 401 (needs verification) depending on business rules
        assert signin_response.status_code in [200, 401]
        
        if signin_response.status_code == 200:
            data = signin_response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"