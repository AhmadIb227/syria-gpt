"""Interface for the TwoFactorAuth repository."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from uuid import UUID


class ITwoFactorAuthRepository(ABC):
    """Interface for the TwoFactorAuth repository."""

    @abstractmethod
    async def create_2fa_code(self, user_id: UUID, code_hash: str, expires_at: Any) -> None:
        """Create a new 2FA code."""
        pass

    @abstractmethod
    async def get_2fa_code_by_user_id(self, user_id: UUID) -> Any:
        """Get the latest 2FA code for a user."""
        pass

    @abstractmethod
    async def mark_code_as_used(self, code_id: UUID) -> None:
        """Mark a 2FA code as used."""
        pass
