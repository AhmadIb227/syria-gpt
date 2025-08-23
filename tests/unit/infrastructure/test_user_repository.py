"""Tests for User Repository implementation."""

import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from domain.entities import User, UserStatus
from infrastructure.database import UserRepositoryImpl


@pytest.mark.asyncio
class TestUserRepository:
    """Test User Repository implementation."""
    
    async def test_create_user(self, user_repository: UserRepositoryImpl):
        """Test creating a user."""
        user_data = {
            "email": "newuser@example.com",
            "password_hash": "hashed_password",
            "first_name": "New",
            "last_name": "User"
        }
        
        user = await user_repository.create(user_data)
        
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.is_email_verified == False
        assert user.is_active == True
        assert user.id is not None
    
    async def test_get_by_id(self, user_repository: UserRepositoryImpl, created_user: User):
        """Test getting user by ID."""
        user = await created_user
        found_user = await user_repository.get_by_id(user.id)
        
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == user.email
    
    async def test_get_by_id_not_found(self, user_repository: UserRepositoryImpl):
        """Test getting user by non-existent ID."""
        non_existent_id = uuid4()
        found_user = await user_repository.get_by_id(non_existent_id)
        
        assert found_user is None
    
    async def test_get_by_email(self, user_repository: UserRepositoryImpl, created_user: User):
        """Test getting user by email."""
        user = await created_user
        found_user = await user_repository.get_by_email(user.email)
        
        assert found_user is not None
        assert found_user.email == user.email
        assert found_user.id == user.id
    
    async def test_get_by_email_not_found(self, user_repository: UserRepositoryImpl):
        """Test getting user by non-existent email."""
        found_user = await user_repository.get_by_email("nonexistent@example.com")
        
        assert found_user is None
    
    async def test_get_by_google_id(self, user_repository: UserRepositoryImpl):
        """Test getting user by Google ID."""
        # Create user with Google ID
        user_data = {
            "email": "google@example.com",
            "google_id": "google123456"
        }
        created_user = await user_repository.create(user_data)
        
        found_user = await user_repository.get_by_google_id("google123456")
        
        assert found_user is not None
        assert found_user.google_id == "google123456"
        assert found_user.id == created_user.id
    
    async def test_get_by_facebook_id(self, user_repository: UserRepositoryImpl):
        """Test getting user by Facebook ID."""
        # Create user with Facebook ID
        user_data = {
            "email": "facebook@example.com",
            "facebook_id": "facebook123456"
        }
        created_user = await user_repository.create(user_data)
        
        found_user = await user_repository.get_by_facebook_id("facebook123456")
        
        assert found_user is not None
        assert found_user.facebook_id == "facebook123456"
        assert found_user.id == created_user.id
    
    async def test_get_by_phone_number(self, user_repository: UserRepositoryImpl):
        """Test getting user by phone number."""
        # Create user with phone number
        user_data = {
            "email": "phone@example.com",
            "phone_number": "+963123456789"
        }
        created_user = await user_repository.create(user_data)
        
        found_user = await user_repository.get_by_phone_number("+963123456789")
        
        assert found_user is not None
        assert found_user.phone_number == "+963123456789"
        assert found_user.id == created_user.id
    
    async def test_update_user(self, user_repository: UserRepositoryImpl, created_user: User):
        """Test updating user data."""
        user = await created_user
        update_data = {
            "first_name": "Updated",
            "is_email_verified": True,
            "status": UserStatus.ACTIVE.value
        }
        
        updated_user = await user_repository.update(user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.first_name == "Updated"
        assert updated_user.is_email_verified == True
        assert updated_user.status == UserStatus.ACTIVE
    
    async def test_update_user_not_found(self, user_repository: UserRepositoryImpl):
        """Test updating non-existent user."""
        non_existent_id = uuid4()
        update_data = {"first_name": "Updated"}
        
        updated_user = await user_repository.update(non_existent_id, update_data)
        
        assert updated_user is None
    
    async def test_delete_user(self, user_repository: UserRepositoryImpl):
        """Test deleting a user."""
        # Create user to delete
        user_data = {
            "email": "todelete@example.com",
            "password_hash": "hashed_password"
        }
        created_user = await user_repository.create(user_data)
        
        # Delete user
        result = await user_repository.delete(created_user.id)
        assert result == True
        
        # Verify user is deleted
        found_user = await user_repository.get_by_id(created_user.id)
        assert found_user is None
    
    async def test_delete_user_not_found(self, user_repository: UserRepositoryImpl):
        """Test deleting non-existent user."""
        non_existent_id = uuid4()
        result = await user_repository.delete(non_existent_id)
        
        assert result == False
    
    async def test_email_exists(self, user_repository: UserRepositoryImpl, created_user: User):
        """Test checking if email exists."""
        user = await created_user
        exists = await user_repository.email_exists(user.email)
        assert exists == True
        
        not_exists = await user_repository.email_exists("nonexistent@example.com")
        assert not_exists == False
    
    async def test_phone_exists(self, user_repository: UserRepositoryImpl):
        """Test checking if phone number exists."""
        # Create user with phone
        user_data = {
            "email": "phonetest@example.com",
            "phone_number": "+963987654321"
        }
        await user_repository.create(user_data)
        
        exists = await user_repository.phone_exists("+963987654321")
        assert exists == True
        
        not_exists = await user_repository.phone_exists("+963000000000")
        assert not_exists == False
    
    async def test_google_id_exists(self, user_repository: UserRepositoryImpl):
        """Test checking if Google ID exists."""
        # Create user with Google ID
        user_data = {
            "email": "googletest@example.com",
            "google_id": "google987654321"
        }
        await user_repository.create(user_data)
        
        exists = await user_repository.google_id_exists("google987654321")
        assert exists == True
        
        not_exists = await user_repository.google_id_exists("google000000000")
        assert not_exists == False
    
    async def test_facebook_id_exists(self, user_repository: UserRepositoryImpl):
        """Test checking if Facebook ID exists."""
        # Create user with Facebook ID
        user_data = {
            "email": "facebooktest@example.com",
            "facebook_id": "facebook987654321"
        }
        await user_repository.create(user_data)
        
        exists = await user_repository.facebook_id_exists("facebook987654321")
        assert exists == True
        
        not_exists = await user_repository.facebook_id_exists("facebook000000000")
        assert not_exists == False
    
    async def test_get_active_users(self, user_repository: UserRepositoryImpl):
        """Test getting active users."""
        # Create active user
        active_user_data = {
            "email": "active@example.com",
            "is_active": True
        }
        await user_repository.create(active_user_data)
        
        # Create inactive user
        inactive_user_data = {
            "email": "inactive@example.com",
            "is_active": False
        }
        await user_repository.create(inactive_user_data)
        
        active_users = await user_repository.get_active_users()
        
        assert len(active_users) >= 1
        for user in active_users:
            assert user.is_active == True
    
    async def test_get_verified_users(self, user_repository: UserRepositoryImpl):
        """Test getting verified users."""
        # Create verified user
        verified_user_data = {
            "email": "verified@example.com",
            "is_email_verified": True
        }
        await user_repository.create(verified_user_data)
        
        # Create unverified user
        unverified_user_data = {
            "email": "unverified@example.com",
            "is_email_verified": False
        }
        await user_repository.create(unverified_user_data)
        
        verified_users = await user_repository.get_verified_users()
        
        assert len(verified_users) >= 1
        for user in verified_users:
            assert user.is_email_verified == True