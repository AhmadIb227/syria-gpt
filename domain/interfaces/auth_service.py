"""Authentication service interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID

from domain.entities import User


class IAuthService(ABC):
    """Interface for authentication service operations."""
    
    @abstractmethod
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Register a new user."""
        pass
    
    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password."""
        pass
    
    @abstractmethod
    async def authenticate_with_google(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate user with Google OAuth."""
        pass
    
    @abstractmethod
    async def authenticate_with_facebook(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate user with Facebook OAuth."""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        pass
    
    @abstractmethod
    async def verify_email(self, token: str) -> Dict[str, str]:
        """Verify user email with token."""
        pass
    
    @abstractmethod
    async def request_password_reset(self, email: str) -> Dict[str, str]:
        """Request password reset."""
        pass
    
    @abstractmethod
    async def confirm_password_reset(self, token: str, new_password: str) -> Dict[str, str]:
        """Confirm password reset."""
        pass
    
    @abstractmethod
    async def change_password(self, user_id: UUID, current_password: str, new_password: str) -> Dict[str, str]:
        """Change user password."""
        pass
    
    @abstractmethod
    async def sign_out_user(self, user_id: UUID, refresh_token: str) -> Dict[str, str]:
        """Sign out user."""
        pass
    
    @abstractmethod
    async def sign_out_all_devices(self, user_id: UUID) -> Dict[str, str]:
        """Sign out user from all devices."""
        pass