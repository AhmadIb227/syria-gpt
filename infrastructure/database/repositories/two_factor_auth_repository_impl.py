"""Implementation of the TwoFactorAuth repository."""

from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import TwoFactorAuth
from domain.interfaces.two_factor_auth_repository import ITwoFactorAuthRepository
from datetime import datetime

class TwoFactorAuthRepositoryImpl(ITwoFactorAuthRepository):
    """Implementation of the TwoFactorAuth repository."""

    def __init__(self, session: Session):
        self.session = session

    async def create_2fa_code(self, user_id: UUID, code_hash: str, expires_at: Any) -> None:
        """Create a new 2FA code."""
        new_code = TwoFactorAuth(
            user_id=user_id,
            code_hash=code_hash,
            expires_at=expires_at
        )
        self.session.add(new_code)
        self.session.commit()

    async def get_2fa_code_by_user_id(self, user_id: UUID) -> Any:
        """Get the latest 2FA code for a user."""
        return self.session.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id,
            TwoFactorAuth.expires_at > datetime.utcnow(),
            TwoFactorAuth.is_used == False
        ).order_by(TwoFactorAuth.created_at.desc()).first()

    async def mark_code_as_used(self, code_id: UUID) -> None:
        """Mark a 2FA code as used."""
        code = self.session.query(TwoFactorAuth).filter(TwoFactorAuth.id == code_id).first()
        if code:
            code.is_used = True
            self.session.commit()
