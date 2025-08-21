"""Token service for JWT operations."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
from uuid import UUID

from config.settings import settings
from infrastructure.database.password_reset_repository import PasswordResetRepository

class TokenService:
    """Service for JWT token operations."""

    def __init__(self, password_reset_repo: PasswordResetRepository):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        self.password_reset_expire_minutes = 60  # مدة صلاحية رابط إعادة التعيين
    
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
    
    def create_password_reset_token(self, user_id: UUID, expire_minutes: int = 60) -> str:
        """Create JWT password reset token."""
        expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
        token = jwt.encode(
            {"sub": str(user_id), "exp": expires_at, "type": "password_reset"},
            self.secret_key,
            algorithm=self.algorithm
        )
        
        self.password_reset_repo.create({
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "is_used": False
        })
        return token
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token with type check."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
            
            return payload
        except JWTError:
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
    
    def get_access_token_expiry(self) -> int:
        """Get access token expiry in seconds."""
        return self.access_token_expire_minutes * 60