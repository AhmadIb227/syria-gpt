"""Tests for User domain entity."""

import pytest
from uuid import uuid4
from domain.entities import User, UserStatus


class TestUserEntity:
    """Test User domain entity."""
    
    def test_user_creation(self):
        """Test user creation with default values."""
        user = User(email="test@example.com")
        
        assert user.email == "test@example.com"
        assert user.is_email_verified == False
        assert user.is_phone_verified == False
        assert user.two_factor_enabled == False
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.is_active == True
    
    def test_user_full_name_property(self):
        """Test full_name property."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )
        assert user.full_name == "John Doe"
        
        user_first_only = User(
            email="test@example.com",
            first_name="John"
        )
        assert user_first_only.full_name == "John"
        
        user_last_only = User(
            email="test@example.com",
            last_name="Doe"
        )
        assert user_last_only.full_name == "Doe"
        
        user_no_name = User(email="test@example.com")
        assert user_no_name.full_name == ""
    
    def test_is_verified_property(self):
        """Test is_verified property."""
        user = User(email="test@example.com")
        assert user.is_verified == False
        
        user.is_email_verified = True
        assert user.is_verified == True
        
        user.is_email_verified = False
        user.is_phone_verified = True
        assert user.is_verified == True
    
    def test_can_login_property(self):
        """Test can_login property."""
        # User with password
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_active=True
        )
        assert user.can_login == True
        
        # User with Google OAuth
        user_google = User(
            email="test@example.com",
            google_id="google123",
            status=UserStatus.ACTIVE,
            is_active=True
        )
        assert user_google.can_login == True
        
        # User with Facebook OAuth
        user_facebook = User(
            email="test@example.com",
            facebook_id="facebook123",
            status=UserStatus.ACTIVE,
            is_active=True
        )
        assert user_facebook.can_login == True
        
        # Inactive user
        user_inactive = User(
            email="test@example.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_active=False
        )
        assert user_inactive.can_login == False
        
        # User without login method
        user_no_login = User(
            email="test@example.com",
            status=UserStatus.ACTIVE,
            is_active=True
        )
        assert user_no_login.can_login == False
    
    def test_activate_method(self):
        """Test activate method."""
        user = User(
            email="test@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            is_active=False
        )
        
        user.activate()
        
        assert user.is_active == True
        assert user.status == UserStatus.ACTIVE
    
    def test_deactivate_method(self):
        """Test deactivate method."""
        user = User(
            email="test@example.com",
            status=UserStatus.ACTIVE,
            is_active=True
        )
        
        user.deactivate()
        
        assert user.is_active == False
        assert user.status == UserStatus.INACTIVE
    
    def test_verify_email_method(self):
        """Test verify_email method."""
        user = User(
            email="test@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            is_email_verified=False
        )
        
        user.verify_email()
        
        assert user.is_email_verified == True
        assert user.status == UserStatus.ACTIVE
    
    def test_verify_phone_method(self):
        """Test verify_phone method."""
        user = User(
            email="test@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            is_phone_verified=False
        )
        
        user.verify_phone()
        
        assert user.is_phone_verified == True
        assert user.status == UserStatus.ACTIVE
    
    def test_enable_two_factor(self):
        """Test enable_two_factor method."""
        user = User(
            email="test@example.com",
            is_email_verified=True,
            two_factor_enabled=False
        )
        
        user.enable_two_factor()
        assert user.two_factor_enabled == True
        
        # Test with unverified user
        unverified_user = User(
            email="test@example.com",
            is_email_verified=False,
            two_factor_enabled=False
        )
        
        with pytest.raises(ValueError, match="User must be verified to enable 2FA"):
            unverified_user.enable_two_factor()
    
    def test_disable_two_factor(self):
        """Test disable_two_factor method."""
        user = User(
            email="test@example.com",
            two_factor_enabled=True
        )
        
        user.disable_two_factor()
        assert user.two_factor_enabled == False
    
    def test_link_google_account(self):
        """Test link_google_account method."""
        user = User(email="test@example.com")
        
        user.link_google_account("google123")
        assert user.google_id == "google123"
        
        # Test with empty Google ID
        with pytest.raises(ValueError, match="Google ID cannot be empty"):
            user.link_google_account("")
    
    def test_link_facebook_account(self):
        """Test link_facebook_account method."""
        user = User(email="test@example.com")
        
        user.link_facebook_account("facebook123")
        assert user.facebook_id == "facebook123"
        
        # Test with empty Facebook ID
        with pytest.raises(ValueError, match="Facebook ID cannot be empty"):
            user.link_facebook_account("")
    
    def test_unlink_google_account(self):
        """Test unlink_google_account method."""
        # User with password and Google
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            google_id="google123"
        )
        
        user.unlink_google_account()
        assert user.google_id is None
        
        # User with only Google (should fail)
        user_google_only = User(
            email="test@example.com",
            google_id="google123"
        )
        
        with pytest.raises(ValueError, match="Cannot unlink Google account - no other login method available"):
            user_google_only.unlink_google_account()
    
    def test_unlink_facebook_account(self):
        """Test unlink_facebook_account method."""
        # User with password and Facebook
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            facebook_id="facebook123"
        )
        
        user.unlink_facebook_account()
        assert user.facebook_id is None
        
        # User with only Facebook (should fail)
        user_facebook_only = User(
            email="test@example.com",
            facebook_id="facebook123"
        )
        
        with pytest.raises(ValueError, match="Cannot unlink Facebook account - no other login method available"):
            user_facebook_only.unlink_facebook_account()