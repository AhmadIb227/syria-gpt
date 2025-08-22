"""Token service for JWT operations."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
from uuid import UUID

from config.settings import settings
from infrastructure.database.password_reset_repository import PasswordResetRepository

import logging

logger = logging.getLogger(__name__)


class TokenService:
    """Service for JWT token operations."""

    def __init__(self, password_reset_repo: PasswordResetRepository):
        self.password_reset_repo = password_reset_repo
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        self.email_verification_expire_hours = settings.EMAIL_VERIFICATION_EXPIRE_HOURS
        self.password_reset_expire_minutes = 60

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token."""
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "type": "refresh",
        }

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_password_reset_token(self, user_id: UUID, expire_minutes: int = 60) -> str:
        """Create JWT password reset token."""
        expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
        token = jwt.encode(
            {"sub": str(user_id), "exp": expires_at, "type": "password_reset"},
            self.secret_key,
            algorithm=self.algorithm,
        )

        self.password_reset_repo.create(
            {"user_id": user_id, "token": token, "expires_at": expires_at, "is_used": False}
        )
        return token

    def create_2fa_token(self, user_id: str) -> str:
        """Create a short-lived token for 2FA verification."""
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=10),  # 2FA token valid for 10 minutes
            "type": "2fa",
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token with type check."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != token_type:
                return None

            return payload
        except JWTError as e:  # <-- عدّل هذا السطر
            logger.error(f"Token verification failed: {e}")  # <-- أضف هذا السطر
            return None

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return user_id if valid."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != "password_reset":
                return None

            db_token = self.password_reset_repo.get_by_token(token)
            if not db_token or db_token.is_used or db_token.expires_at < datetime.utcnow():
                return None

            self.password_reset_repo.mark_used(db_token.id)
            return payload.get("sub")  # user_id
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def generate_verification_token(self, user_id: str) -> str:
        """Generate a secure JWT for email verification."""
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.email_verification_expire_hours),
            "type": "email_verification",
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_verification_token(self, token: str) -> Optional[str]:
        """Verify the email verification token and return the user ID."""
        payload = self.verify_token(token, token_type="email_verification")
        if not payload:
            return None
        return payload.get("sub")

    def get_access_token_expiry(self) -> int:
        """Get access token expiry in seconds."""
        return self.access_token_expire_minutes * 60
