"""User repository interface - defines contract for data access."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from uuid import UUID

from domain.entities import User


class IUserRepository(ABC):
    """Interface for user repository operations."""
    
    @abstractmethod
    async def create(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        pass
    
    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        pass
    
    @abstractmethod
    async def get_by_facebook_id(self, facebook_id: str) -> Optional[User]:
        """Get user by Facebook ID."""
        pass
    
    @abstractmethod
    async def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        pass
    
    @abstractmethod
    async def update(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user data."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user."""
        pass
    
    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        pass
    
    @abstractmethod
    async def phone_exists(self, phone_number: str) -> bool:
        """Check if phone number already exists."""
        pass
    
    @abstractmethod
    async def google_id_exists(self, google_id: str) -> bool:
        """Check if Google ID already exists."""
        pass
    
    @abstractmethod
    async def facebook_id_exists(self, facebook_id: str) -> bool:
        """Check if Facebook ID already exists."""
        pass
    
    @abstractmethod
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users."""
        pass
    
    @abstractmethod
    async def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get email-verified users."""
        pass