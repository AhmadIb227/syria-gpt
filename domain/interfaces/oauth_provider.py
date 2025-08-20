"""OAuth provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IOAuthProvider(ABC):
    """Interface for OAuth providers (Google, Facebook, etc.)."""
    
    @abstractmethod
    def get_authorization_url(self) -> str:
        """Get OAuth authorization URL."""
        pass
    
    @abstractmethod
    async def exchange_code_for_user_info(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for user information."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name."""
        pass