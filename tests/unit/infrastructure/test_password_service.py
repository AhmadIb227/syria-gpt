"""Tests for Password Service."""

import pytest
from infrastructure.services import PasswordService


class TestPasswordService:
    """Test Password Service."""
    
    def test_hash_password(self, password_service: PasswordService):
        """Test password hashing."""
        password = "testpassword123"
        hashed = password_service.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        assert hashed.startswith("$2b$")  # bcrypt identifier
    
    def test_verify_password_correct(self, password_service: PasswordService):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = password_service.hash_password(password)
        
        is_valid = password_service.verify_password(password, hashed)
        assert is_valid == True
    
    def test_verify_password_incorrect(self, password_service: PasswordService):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = password_service.hash_password(password)
        
        is_valid = password_service.verify_password(wrong_password, hashed)
        assert is_valid == False
    
    def test_hash_different_passwords(self, password_service: PasswordService):
        """Test that same passwords produce different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)
        
        assert hash1 != hash2  # Different due to random salt
        
        # But both should verify correctly
        assert password_service.verify_password(password, hash1) == True
        assert password_service.verify_password(password, hash2) == True