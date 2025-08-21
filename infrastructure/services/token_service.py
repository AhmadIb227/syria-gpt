"""Token service for JWT operations."""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
import logging
from config.settings import settings

logger = logging.getLogger(__name__)
class TokenService:
    """Service for JWT token operations."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        
        self.email_verification_expire_hours = settings.EMAIL_VERIFICATION_EXPIRE_HOURS
    
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
            "type": "refresh"
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_2fa_token(self, user_id: str) -> str:
        """Create a short-lived token for 2FA verification."""
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=10),  # 2FA token valid for 10 minutes
            "type": "2fa",
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != token_type:
                return None

            return payload
        except JWTError as e: # <-- عدّل هذا السطر
            logger.error(f"Token verification failed: {e}") # <-- أضف هذا السطر
            return None
    
    def generate_verification_token(self, user_id: str) -> str:
        """Generate a secure JWT for email verification."""
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.email_verification_expire_hours),
            "type": "email_verification"
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