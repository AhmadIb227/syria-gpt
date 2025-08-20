"""Token service for JWT operations."""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt

from config.settings import settings


class TokenService:
    """Service for JWT token operations."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
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
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
            
            return payload
        except JWTError:
            return None
    
    def generate_verification_token(self) -> str:
        """Generate secure verification token."""
        return secrets.token_urlsafe(32)
    
    def verify_verification_token(self, token: str) -> Optional[str]:
        """Verify verification token (simplified - in real app would be stored in DB)."""
        # This is a simplified implementation
        # In a real application, you would store verification tokens in the database
        # with expiration times and mark them as used when verified
        return None  # Placeholder
    
    def get_access_token_expiry(self) -> int:
        """Get access token expiry in seconds."""
        return self.access_token_expire_minutes * 60