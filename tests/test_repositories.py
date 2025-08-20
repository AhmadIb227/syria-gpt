"""Unit tests for repositories."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config.model import Base, User, EmailVerification, PasswordReset, RefreshToken
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
def user_repo(db_session):
    """Create user repository."""
    return UserRepository(db_session)


@pytest.fixture
def email_verification_repo(db_session):
    """Create email verification repository."""
    return EmailVerificationRepository(db_session)


@pytest.fixture
def password_reset_repo(db_session):
    """Create password reset repository."""
    return PasswordResetRepository(db_session)


@pytest.fixture
def refresh_token_repo(db_session):
    """Create refresh token repository."""
    return RefreshTokenRepository(db_session)


@pytest.fixture
def auth_manager(db_session):
    """Create auth repository manager."""
    return AuthRepositoryManager(db_session)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password_hash": "hashed_password_123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890"
    }


class TestUserRepository:
    """Test user repository functionality."""
    
    def test_create_user(self, user_repo, sample_user_data):
        """Test creating a new user."""
        user = user_repo.create_user(sample_user_data)
        
        assert user.id is not None
        assert user.email == sample_user_data["email"]
        assert user.first_name == sample_user_data["first_name"]
        assert user.status == "pending_verification"
        assert user.is_active is True
        assert user.is_email_verified is False
    
    def test_get_by_email(self, user_repo, sample_user_data):
        """Test getting user by email."""
        created_user = user_repo.create_user(sample_user_data)
        
        found_user = user_repo.get_by_email(sample_user_data["email"])
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == sample_user_data["email"]
    
    def test_get_by_email_not_found(self, user_repo):
        """Test getting user by email when not found."""
        found_user = user_repo.get_by_email("nonexistent@example.com")
        assert found_user is None
    
    def test_email_exists(self, user_repo, sample_user_data):
        """Test checking if email exists."""
        assert user_repo.email_exists(sample_user_data["email"]) is False
        
        user_repo.create_user(sample_user_data)
        
        assert user_repo.email_exists(sample_user_data["email"]) is True
        assert user_repo.email_exists("other@example.com") is False
    
    def test_phone_exists(self, user_repo, sample_user_data):
        """Test checking if phone exists."""
        phone = sample_user_data["phone_number"]
        assert user_repo.phone_exists(phone) is False
        
        user_repo.create_user(sample_user_data)
        
        assert user_repo.phone_exists(phone) is True
        assert user_repo.phone_exists("+9876543210") is False
    
    def test_update_verification_status(self, user_repo, sample_user_data):
        """Test updating user verification status."""
        user = user_repo.create_user(sample_user_data)
        
        updated_user = user_repo.update_verification_status(
            user.id, 
            email_verified=True
        )
        
        assert updated_user.is_email_verified is True
        assert updated_user.status == "active"
    
    def test_activate_deactivate_user(self, user_repo, sample_user_data):
        """Test activating and deactivating user."""
        user = user_repo.create_user(sample_user_data)
        
        # Deactivate
        deactivated_user = user_repo.deactivate_user(user.id)
        assert deactivated_user.is_active is False
        assert deactivated_user.status == "inactive"
        
        # Activate
        activated_user = user_repo.activate_user(user.id)
        assert activated_user.is_active is True
        assert activated_user.status == "active"
    
    def test_search_users(self, user_repo):
        """Test searching users."""
        # Create test users
        user1_data = {
            "email": "john.doe@example.com",
            "password_hash": "hash1",
            "first_name": "John",
            "last_name": "Doe"
        }
        user2_data = {
            "email": "jane.smith@example.com",
            "password_hash": "hash2",
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        user_repo.create_user(user1_data)
        user_repo.create_user(user2_data)
        
        # Search by first name
        results = user_repo.search_users("John")
        assert len(results) == 1
        assert results[0].first_name == "John"
        
        # Search by email domain
        results = user_repo.search_users("example.com")
        assert len(results) == 2
    
    def test_count_active_users(self, user_repo, sample_user_data):
        """Test counting active users."""
        assert user_repo.count_active_users() == 0
        
        # Create active user
        user1 = user_repo.create_user(sample_user_data)
        assert user_repo.count_active_users() == 1
        
        # Create another user and deactivate
        user2_data = sample_user_data.copy()
        user2_data["email"] = "user2@example.com"
        user2 = user_repo.create_user(user2_data)
        user_repo.deactivate_user(user2.id)
        
        assert user_repo.count_active_users() == 1


class TestEmailVerificationRepository:
    """Test email verification repository functionality."""
    
    def test_create_verification(self, email_verification_repo, user_repo, sample_user_data):
        """Test creating email verification token."""
        user = user_repo.create_user(sample_user_data)
        token = "verification_token_123"
        
        verification = email_verification_repo.create_verification(
            user.id, token, 24
        )
        
        assert verification.id is not None
        assert verification.user_id == user.id
        assert verification.token == token
        assert verification.is_used is False
        assert verification.expires_at > datetime.utcnow()
    
    def test_get_by_token(self, email_verification_repo, user_repo, sample_user_data):
        """Test getting verification by token."""
        user = user_repo.create_user(sample_user_data)
        token = "verification_token_123"
        
        created_verification = email_verification_repo.create_verification(
            user.id, token, 24
        )
        
        found_verification = email_verification_repo.get_by_token(token)
        
        assert found_verification is not None
        assert found_verification.id == created_verification.id
        assert found_verification.token == token
    
    def test_is_valid_token(self, email_verification_repo, user_repo, sample_user_data):
        """Test checking if token is valid."""
        user = user_repo.create_user(sample_user_data)
        token = "verification_token_123"
        
        # Token doesn't exist
        assert email_verification_repo.is_valid_token(token) is False
        
        # Create valid token
        email_verification_repo.create_verification(user.id, token, 24)
        assert email_verification_repo.is_valid_token(token) is True
        
        # Mark as used
        email_verification_repo.mark_as_used(token)
        assert email_verification_repo.is_valid_token(token) is False
    
    def test_mark_as_used(self, email_verification_repo, user_repo, sample_user_data):
        """Test marking token as used."""
        user = user_repo.create_user(sample_user_data)
        token = "verification_token_123"
        
        email_verification_repo.create_verification(user.id, token, 24)
        
        updated_verification = email_verification_repo.mark_as_used(token)
        
        assert updated_verification.is_used is True
    
    def test_cleanup_expired(self, email_verification_repo, user_repo, sample_user_data):
        """Test cleaning up expired tokens."""
        user = user_repo.create_user(sample_user_data)
        
        # Create expired token (expires in the past)
        expired_verification = EmailVerification(
            user_id=user.id,
            token="expired_token",
            expires_at=datetime.utcnow() - timedelta(hours=1),
            is_used=False
        )
        email_verification_repo.db.add(expired_verification)
        email_verification_repo.db.commit()
        
        # Create valid token
        email_verification_repo.create_verification(user.id, "valid_token", 24)
        
        # Cleanup expired
        cleaned_count = email_verification_repo.cleanup_expired()
        
        assert cleaned_count == 1
        assert email_verification_repo.get_by_token("expired_token") is None
        assert email_verification_repo.get_by_token("valid_token") is not None


class TestRefreshTokenRepository:
    """Test refresh token repository functionality."""
    
    def test_create_refresh_token(self, refresh_token_repo, user_repo, sample_user_data):
        """Test creating refresh token."""
        user = user_repo.create_user(sample_user_data)
        token = "refresh_token_123"
        
        refresh_token = refresh_token_repo.create_refresh_token(
            user.id, token, 7
        )
        
        assert refresh_token.id is not None
        assert refresh_token.user_id == user.id
        assert refresh_token.token == token
        assert refresh_token.is_revoked is False
        assert refresh_token.expires_at > datetime.utcnow()
    
    def test_get_by_token(self, refresh_token_repo, user_repo, sample_user_data):
        """Test getting refresh token by token string."""
        user = user_repo.create_user(sample_user_data)
        token = "refresh_token_123"
        
        created_token = refresh_token_repo.create_refresh_token(user.id, token, 7)
        found_token = refresh_token_repo.get_by_token(token)
        
        assert found_token is not None
        assert found_token.id == created_token.id
    
    def test_is_valid_token(self, refresh_token_repo, user_repo, sample_user_data):
        """Test checking if refresh token is valid."""
        user = user_repo.create_user(sample_user_data)
        token = "refresh_token_123"
        
        # Token doesn't exist
        assert refresh_token_repo.is_valid_token(token) is False
        
        # Create valid token
        refresh_token_repo.create_refresh_token(user.id, token, 7)
        assert refresh_token_repo.is_valid_token(token) is True
        
        # Revoke token
        refresh_token_repo.revoke_token(token)
        assert refresh_token_repo.is_valid_token(token) is False
    
    def test_revoke_user_tokens(self, refresh_token_repo, user_repo, sample_user_data):
        """Test revoking all user tokens."""
        user = user_repo.create_user(sample_user_data)
        
        # Create multiple tokens
        refresh_token_repo.create_refresh_token(user.id, "token1", 7)
        refresh_token_repo.create_refresh_token(user.id, "token2", 7)
        
        # Revoke all
        revoked_count = refresh_token_repo.revoke_user_tokens(user.id)
        
        assert revoked_count == 2
        assert refresh_token_repo.is_valid_token("token1") is False
        assert refresh_token_repo.is_valid_token("token2") is False


class TestAuthRepositoryManager:
    """Test auth repository manager functionality."""
    
    def test_revoke_all_user_tokens(self, auth_manager, user_repo, sample_user_data):
        """Test revoking all tokens for a user."""
        user = user_repo.create_user(sample_user_data)
        
        # Create tokens in all repositories
        auth_manager.email_verification.create_verification(user.id, "email_token", 24)
        auth_manager.password_reset.create_reset_token(user.id, "reset_token", 1)
        auth_manager.refresh_token.create_refresh_token(user.id, "refresh_token", 7)
        
        # Revoke all
        results = auth_manager.revoke_all_user_tokens(user.id)
        
        assert results["email_verifications"] == 1
        assert results["password_resets"] == 1
        assert results["refresh_tokens"] == 1
        
        # Verify tokens are revoked/used
        assert not auth_manager.email_verification.is_valid_token("email_token")
        assert not auth_manager.password_reset.is_valid_token("reset_token")
        assert not auth_manager.refresh_token.is_valid_token("refresh_token")