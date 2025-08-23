"""Tests for Auth Application Service."""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from application import AuthApplicationService
from domain.use_cases import AuthUseCases
from infrastructure.external_services import GoogleOAuthProvider, FacebookOAuthProvider


class TestAuthApplicationService:
    """Test Auth Application Service."""
    
    @pytest.fixture
    def mock_auth_use_cases(self):
        """Create mock auth use cases."""
        mock = Mock(spec=AuthUseCases)
        mock.register_user = AsyncMock()
        mock.authenticate_user = AsyncMock()
        mock.authenticate_with_oauth = AsyncMock()
        mock.verify_email = AsyncMock()
        mock.change_password = AsyncMock()
        mock.request_password_reset = AsyncMock()
        mock.confirm_password_reset = AsyncMock()
        return mock
    
    @pytest.fixture
    def auth_app_service(self, mock_auth_use_cases, mock_google_provider, mock_facebook_provider):
        """Create auth application service with mocked dependencies."""
        return AuthApplicationService(
            auth_use_cases=mock_auth_use_cases,
            google_provider=mock_google_provider,
            facebook_provider=mock_facebook_provider
        )
    
    @pytest.mark.asyncio
    async def test_register_user(self, auth_app_service: AuthApplicationService, mock_auth_use_cases):
        """Test user registration."""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test"
        }
        expected_result = {"message": "User registered successfully", "user_id": "123"}
        mock_auth_use_cases.register_user.return_value = expected_result
        
        result = await auth_app_service.register_user(user_data)
        
        mock_auth_use_cases.register_user.assert_called_once_with(user_data)
        assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_authenticate_user(self, auth_app_service: AuthApplicationService, mock_auth_use_cases):
        """Test user authentication."""
        email = "test@example.com"
        password = "testpassword123"
        expected_result = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "token_type": "bearer",
            "expires_in": 1800
        }
        mock_auth_use_cases.authenticate_user.return_value = expected_result
        
        result = await auth_app_service.authenticate_user(email, password)
        
        mock_auth_use_cases.authenticate_user.assert_called_once_with(email, password)
        assert result == expected_result
    
    def test_get_google_auth_url(self, auth_app_service: AuthApplicationService, mock_google_provider):
        """Test getting Google OAuth URL."""
        expected_url = "https://accounts.google.com/oauth/authorize?..."
        mock_google_provider.get_authorization_url.return_value = expected_url
        
        result = auth_app_service.get_google_auth_url()
        
        mock_google_provider.get_authorization_url.assert_called_once()
        assert result == {
            "auth_url": expected_url,
            "provider": "google"
        }
    
    def test_get_facebook_auth_url(self, auth_app_service: AuthApplicationService, mock_facebook_provider):
        """Test getting Facebook OAuth URL."""
        expected_url = "https://www.facebook.com/dialog/oauth?..."
        mock_facebook_provider.get_authorization_url.return_value = expected_url
        
        result = auth_app_service.get_facebook_auth_url()
        
        mock_facebook_provider.get_authorization_url.assert_called_once()
        assert result == {
            "auth_url": expected_url,
            "provider": "facebook"
        }
    
    @pytest.mark.asyncio
    async def test_authenticate_with_google(self, auth_app_service: AuthApplicationService, mock_auth_use_cases, mock_google_provider):
        """Test Google OAuth authentication."""
        auth_code = "google_auth_code_123"
        expected_result = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "token_type": "bearer",
            "expires_in": 1800
        }
        mock_auth_use_cases.authenticate_with_oauth.return_value = expected_result
        
        result = await auth_app_service.authenticate_with_google(auth_code)
        
        mock_auth_use_cases.authenticate_with_oauth.assert_called_once_with(
            mock_google_provider, 
            auth_code
        )
        assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_authenticate_with_facebook(self, auth_app_service: AuthApplicationService, mock_auth_use_cases, mock_facebook_provider):
        """Test Facebook OAuth authentication."""
        auth_code = "facebook_auth_code_123"
        expected_result = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123", 
            "token_type": "bearer",
            "expires_in": 1800
        }
        mock_auth_use_cases.authenticate_with_oauth.return_value = expected_result
        
        result = await auth_app_service.authenticate_with_facebook(auth_code)
        
        mock_auth_use_cases.authenticate_with_oauth.assert_called_once_with(
            mock_facebook_provider,
            auth_code
        )
        assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_verify_email(self, auth_app_service: AuthApplicationService, mock_auth_use_cases):
        """Test email verification."""
        token = "verification_token_123"
        expected_result = {"message": "Email verified successfully"}
        mock_auth_use_cases.verify_email.return_value = expected_result
        
        result = await auth_app_service.verify_email(token)
        
        mock_auth_use_cases.verify_email.assert_called_once_with(token)
        assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_change_password(self, auth_app_service: AuthApplicationService, mock_auth_use_cases):
        """Test password change."""
        user_id = uuid4()
        current_password = "currentpassword"
        new_password = "newpassword123"
        expected_result = {"message": "Password changed successfully"}
        mock_auth_use_cases.change_password.return_value = expected_result
        
        result = await auth_app_service.change_password(
            user_id, 
            current_password, 
            new_password
        )
        
        mock_auth_use_cases.change_password.assert_called_once_with(
            user_id,
            current_password,
            new_password
        )
        assert result == expected_result
        
    @pytest.mark.asyncio
    async def test_request_password_reset(self, auth_app_service: AuthApplicationService, mock_auth_use_cases):
        """Test requesting password reset."""
        email = "test@example.com"
        expected_result = {"message": "Password reset instructions sent to your email"}
        mock_auth_use_cases.request_password_reset.return_value = expected_result

        result = await auth_app_service.request_password_reset(email)

        mock_auth_use_cases.request_password_reset.assert_called_once_with(email)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_confirm_password_reset(self, auth_app_service: AuthApplicationService, mock_auth_use_cases):
        """Test confirming password reset."""
        token = "reset_token_123"
        new_password = "newpassword123"
        expected_result = {"message": "Password has been reset successfully"}
        mock_auth_use_cases.confirm_password_reset.return_value = expected_result

        result = await auth_app_service.confirm_password_reset(token, new_password)

        mock_auth_use_cases.confirm_password_reset.assert_called_once_with(token, new_password)
        assert result == expected_result