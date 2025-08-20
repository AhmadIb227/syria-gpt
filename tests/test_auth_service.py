"""Unit tests for authentication service."""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config.model import Base
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from repositories.auth_repositories import (
    EmailVerificationRepository,
    PasswordResetRepository,
    RefreshTokenRepository,
    AuthRepositoryManager
)


@pytest.fixture
def db_session():
    """Create test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_service(db_session):
    """Create auth service with repositories."""
    user_repo = UserRepository(db_session)
    email_verification_repo = EmailVerificationRepository(db_session)
    password_reset_repo = PasswordResetRepository(db_session)
    refresh_token_repo = RefreshTokenRepository(db_session)
    auth_manager = AuthRepositoryManager(db_session)
    
    return AuthService(
        user_repo,
        email_verification_repo,
        password_reset_repo,
        refresh_token_repo,
        auth_manager
    )


@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890"
    }


class TestAuthService:
    """Test authentication service functionality."""
    
    @patch('config.auth.AuthUtils.get_password_hash')
    @patch('config.auth.AuthUtils.generate_verification_token')
    @patch('config.email_service.email_service.send_verification_email')
    def test_register_user_success(
        self, 
        mock_send_email,
        mock_generate_token,
        mock_hash_password,
        auth_service, 
        sample_user_data
    ):
        """Test successful user registration."""
        mock_hash_password.return_value = "hashed_password_123"
        mock_generate_token.return_value = "verification_token_123"
        
        result = auth_service.register_user(sample_user_data)
        
        assert "message" in result
        assert "user_id" in result
        assert "successfully" in result["message"]
        
        # Verify password was hashed
        mock_hash_password.assert_called_once_with(sample_user_data["password"])
        
        # Verify verification token was generated
        mock_generate_token.assert_called_once()
        
        # Verify email was sent
        mock_send_email.assert_called_once_with(
            sample_user_data["email"], 
            "verification_token_123"
        )
    
    def test_register_user_duplicate_email(self, auth_service, sample_user_data):
        """Test registering user with duplicate email."""
        # First registration should succeed
        with patch('config.auth.AuthUtils.get_password_hash', return_value="hashed_password"):
            with patch('config.auth.AuthUtils.generate_verification_token', return_value="token"):
                with patch('config.email_service.email_service.send_verification_email'):
                    auth_service.register_user(sample_user_data)
        
        # Second registration should fail
        with pytest.raises(HTTPException) as exc_info:
            with patch('config.auth.AuthUtils.get_password_hash', return_value="hashed_password"):
                auth_service.register_user(sample_user_data)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)
    
    @patch('config.auth.AuthUtils.verify_password')
    @patch('config.auth.AuthUtils.create_access_token')
    @patch('config.auth.AuthUtils.create_refresh_token')
    def test_authenticate_user_success(
        self,
        mock_create_refresh,
        mock_create_access,
        mock_verify_password,
        auth_service,
        sample_user_data
    ):
        """Test successful user authentication."""
        # First create a user
        with patch('config.auth.AuthUtils.get_password_hash', return_value="hashed_password"):
            with patch('config.auth.AuthUtils.generate_verification_token', return_value="token"):
                with patch('config.email_service.email_service.send_verification_email'):
                    auth_service.register_user(sample_user_data)
        
        # Mock authentication methods
        mock_verify_password.return_value = True
        mock_create_access.return_value = "access_token_123"
        mock_create_refresh.return_value = "refresh_token_123"
        
        result = auth_service.authenticate_user(
            sample_user_data["email"],
            sample_user_data["password"]
        )
        
        assert result["access_token"] == "access_token_123"
        assert result["refresh_token"] == "refresh_token_123"
        assert result["token_type"] == "bearer"
        assert "expires_in" in result
        
        mock_verify_password.assert_called_once()
        mock_create_access.assert_called_once()
        mock_create_refresh.assert_called_once()
    
    def test_authenticate_user_invalid_credentials(self, auth_service):
        """Test authentication with invalid credentials."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.authenticate_user("nonexistent@example.com", "password")
        
        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in str(exc_info.value.detail)
    
    @patch('config.auth.AuthUtils.verify_password')
    def test_authenticate_user_wrong_password(
        self,
        mock_verify_password,
        auth_service,
        sample_user_data
    ):
        """Test authentication with wrong password."""
        # First create a user
        with patch('config.auth.AuthUtils.get_password_hash', return_value="hashed_password"):
            with patch('config.auth.AuthUtils.generate_verification_token', return_value="token"):
                with patch('config.email_service.email_service.send_verification_email'):
                    auth_service.register_user(sample_user_data)
        
        mock_verify_password.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.authenticate_user(
                sample_user_data["email"],
                "wrong_password"
            )
        
        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in str(exc_info.value.detail)
    
    def test_verify_email_success(self, auth_service, sample_user_data):
        """Test successful email verification."""
        # Create user and verification token
        with patch('config.auth.AuthUtils.get_password_hash', return_value="hashed_password"):
            with patch('config.auth.AuthUtils.generate_verification_token', return_value="token_123"):
                with patch('config.email_service.email_service.send_verification_email'):
                    user_result = auth_service.register_user(sample_user_data)
        
        # Verify email
        result = auth_service.verify_email("token_123")
        
        assert result["message"] == "Email verified successfully"
        
        # Check that user is now verified
        user = auth_service.user_repo.get_by_email(sample_user_data["email"])
        assert user.is_email_verified is True
        assert user.status == "active"
    
    def test_verify_email_invalid_token(self, auth_service):
        """Test email verification with invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_email("invalid_token")
        
        assert exc_info.value.status_code == 400
        assert "Invalid or expired verification token" in str(exc_info.value.detail)
    
    @patch('config.auth.AuthUtils.generate_reset_token')
    @patch('config.email_service.email_service.send_password_reset_email')
    def test_request_password_reset(
        self,
        mock_send_email,
        mock_generate_token,
        auth_service,
        sample_user_data
    ):
        """Test password reset request."""
        # Create user
        with patch('config.auth.AuthUtils.get_password_hash', return_value="hashed_password"):
            with patch('config.auth.AuthUtils.generate_verification_token', return_value="token"):
                with patch('config.email_service.email_service.send_verification_email'):
                    auth_service.register_user(sample_user_data)
        
        mock_generate_token.return_value = "reset_token_123"
        
        result = auth_service.request_password_reset(sample_user_data["email"])
        
        assert "reset link has been sent" in result["message"]
        mock_generate_token.assert_called_once()
        mock_send_email.assert_called_once_with(
            sample_user_data["email"],
            "reset_token_123"
        )
    
    def test_request_password_reset_nonexistent_email(self, auth_service):
        """Test password reset request for nonexistent email."""
        result = auth_service.request_password_reset("nonexistent@example.com")
        
        # Should return success message for security reasons
        assert "reset link has been sent" in result["message"]