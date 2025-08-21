"""Tests for Token Service."""

import pytest
import uuid
from datetime import datetime, timedelta
from infrastructure.services import TokenService


class TestTokenService:
    """Test Token Service."""
    
    def test_create_access_token(self, token_service: TokenService):
        """Test creating access token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = token_service.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
    
    def test_create_refresh_token(self, token_service: TokenService):
        """Test creating refresh token."""
        user_id = "user123"
        token = token_service.create_refresh_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50
    
    def test_verify_access_token_valid(self, token_service: TokenService):
        """Test verifying valid access token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = token_service.create_access_token(data)
        
        payload = token_service.verify_token(token, "access")
        
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
        assert "exp" in payload
    
    def test_verify_refresh_token_valid(self, token_service: TokenService):
        """Test verifying valid refresh token."""
        user_id = "user123"
        token = token_service.create_refresh_token(user_id)
        
        payload = token_service.verify_token(token, "refresh")
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_verify_token_invalid(self, token_service: TokenService):
        """Test verifying invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = token_service.verify_token(invalid_token, "access")
        
        assert payload is None
    
    def test_verify_token_wrong_type(self, token_service: TokenService):
        """Test verifying token with wrong type."""
        data = {"sub": "user123"}
        access_token = token_service.create_access_token(data)
        
        # Try to verify access token as refresh token
        payload = token_service.verify_token(access_token, "refresh")
        
        assert payload is None
    
    def test_generate_verification_token(self, token_service: TokenService):
        """Test generating verification token."""
        user_id = str(uuid.uuid4()) # إضافة user_id وهمي
        token = token_service.generate_verification_token(user_id) # تمرير الـ user_id
        assert isinstance(token, str)
        # يمكنك إضافة المزيد من التأكيدات هنا
    
    def test_generate_verification_token_unique(self, token_service: TokenService):
        """Test that verification tokens are unique."""
        user_id_1 = str(uuid.uuid4()) # إضافة user_id وهمي
        user_id_2 = str(uuid.uuid4()) # إضافة user_id وهمي آخر
        token1 = token_service.generate_verification_token(user_id_1) # تمرير الـ user_id
        token2 = token_service.generate_verification_token(user_id_2) # تمرير الـ user_id
        assert token1 != token2    
    
    def test_get_access_token_expiry(self, token_service: TokenService):
        """Test getting access token expiry."""
        expiry = token_service.get_access_token_expiry()
        
        assert expiry > 0
        assert isinstance(expiry, int)
        # Should be 30 minutes * 60 seconds = 1800 seconds by default
        assert expiry == 30 * 60


    def test_verify_verification_token_valid(self, token_service: TokenService):
        """Test verifying a valid verification token."""
        user_id = str(uuid.uuid4()) # إضافة user_id وهمي
        token = token_service.generate_verification_token(user_id) # تمرير الـ user_id
        decoded_user_id = token_service.verify_verification_token(token)
        assert decoded_user_id == user_id    

    